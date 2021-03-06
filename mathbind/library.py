#!/usr/bin/env python3

import json
from path import Path
import os
from mathbind.types import BasicType, VoidType
from mathbind.compilers.compiler import Compiler


class FunctionObject:
    """
    Represents a function object.
    """

    def __init__(self, func_name, return_type, argnames, args):
        self.func_name = func_name
        self.return_type = return_type
        self.argnames = argnames
        self.args = args

    def __eq__(self, other):
        return (
            self.func_name == other.func_name and
            self.return_type == other.return_type and
            self.argnames == other.argnames and
            self.args == other.args)

    def __repr__(self):
        r = 'FunctionObject(func_name={self.func_name}, return_type={self.return_type}, argnames={self.argnames}, args={self.args}'
        return r.format(self=self)

    def copy(self):
        return FunctionObject(self.func_name, self.return_type, self.argnames, self.args)

    def func_str(self, tab='', suffix=None):
        """
        Returns the C code for Mathematica to interact with the function.
        Args:
        - tab (str): string to add at the beginning of each line.
        - suffix: suffix to add after the variable
        """
        if suffix is None:
            suffix = self.default_suffix
        header = ('DLLEXPORT int math_{self.func_name}{suffix}(WolframLibraryData libData{suffix}, '
                  'mint Argc{suffix}, MArgument *Args{suffix}, MArgument Res{suffix}) {{\n')
        header = header.format(self=self, suffix=suffix)

        args_text = ''
        after_code = ''
        args_param = []
        for i, (argname, arg) in enumerate(zip(self.argnames, self.args)):
            args_text += arg.retrieve_cstr(argname, i, tab, suffix)
            args_param += [arg.pass_cstr(argname)]
            after_code += arg.after_cstr(argname, tab, suffix)
        func_call = '{self.func_name}({args_param})'.format(self=self, args_param=', '.join(args_param))

        return_text = self.return_type.return_cstr(func_call, tab, suffix)
        footer = '{tab}return LIBRARY_NO_ERROR;\n}}'.format(tab=tab)

        return (header + args_text + return_text + after_code + footer)

    @classmethod
    def from_dict(self, d):
        """
        Returns a new FunctionObject from the dictionary.

        :param d: dictionary with the function definitions. Must have the form
        {
            "name": "FUNCTION_NAME",
            "args": [
                {"name": "arg1_name", type: "arg1_type"}
                ...
                ]
        }
        :return: FunctionObject
        """
        func_name = d['name']
        return_type = BasicType.from_str(d['return'])

        arg_names = [arg['name'] for arg in d['args']]
        arg_types = [BasicType.from_str(arg['type']) for arg in d['args']]

        return FunctionObject(func_name, return_type, arg_names, arg_types)

    @classmethod
    def from_str(self, s):
        """
        Returns a new FunctionObject from the string.

        :param s: prototype declaration. Example:
        - int func1(double foo);'
        :return: FunctionObject
        """
        if s.count('(') != 1 or s.count(')') != 1:
            raise ValueError('Too much parenthesis')
        par1, par2 = s.index('('), s.index(')')
        if par1 > par2:
            raise ValueError('Displaced parenthesis')

        *type_words, func_name = s[: par1].split()
        args = s[par1 + 1: par2].split(',')

        if s[par2 + 1:].replace(';', '').strip():
            raise ValueError('Displaced comma')

        d = {}
        d['name'] = func_name
        d['return'] = ' '.join(type_words)
        args_types = [BasicType.from_prototype_cstr(arg) for arg in args]
        d['args'] = [{'name': arg[1], 'type': arg[0].typename} for arg in args_types]

        return FunctionObject.from_dict(d)

    @classmethod
    def from_obj(self, obj):
        """
        Tries to call FunctionObject.from_dict() and if it raises an error
        calls FunctionObject.from_str().
        """
        if isinstance(obj, FunctionObject):
            return obj.copy()

        try:
            return FunctionObject.from_dict(obj)
        except (KeyError, TypeError):
            return FunctionObject.from_str(obj)

    def prototype_cstr(self):
        """
        Returns a prototype of the function.
        """
        args = []
        for argname, arg in zip(self.argnames, self.args):
            args += [arg.prototype_cstr(argname)]
        args = ', '.join(args)

        return_type = self.return_type.prototype_return_cstr()
        return return_type + ' ' + self.func_name + '(' + args + ');\n'

    def math_load(self, libname, suffix=None):
        """
        Returns a Mathematica string to load the function from the library.
        """
        arg_code = ', '.join(arg.math_name for arg in self.args)
        ret_code = self.return_type.math_name
        func_name = self.func_name
        func_math_name = self.func_name.replace('_', '')
        if suffix is None:
            suffix = BasicType.default_suffix
        form = '{func_math_name}{suffix} = LibraryFunctionLoad["{libname}", "math_{func_name}{suffix}", {{{arg_code}}}, {ret_code}];\n'
        return form.format(**locals())

    def math_str(self, libname, tab='', suffix=None):
        """
        Return the full Mathematica code to link the function from the library.
        """
        if suffix is None:
            suffix = BasicType.default_suffix
        math_load = self.math_load(libname, suffix)
        arg_code = ''.join(arg.before_mathstr(argname, tab, suffix)
                           for arg, argname in zip(self.args, self.argnames))

        args_prototype = ', '.join(argname + '_' for argname in self.argnames)
        mod_var_names = ', '.join(['return' + suffix] +
                              [argname + suffix for argname in self.argnames])
        return_var_names = ', '.join((['return' + suffix] if self.return_type != VoidType('void') else []) +
                              [argname + suffix
                               for argname, arg in zip(self.argnames, self.args)
                               if arg.should_return])
        arg_names = ', '.join(argname + suffix for argname in self.argnames)
        func_name = self.func_name.replace('_', '')

        func_code = (
            '{func_name}[{args_prototype}] := Module[{{{mod_var_names}}},\n'
            '{arg_code}'
            '{tab}return{suffix} = {func_name}{suffix}[{arg_names}];\n'
            '{tab}{{{return_var_names}}}\n'
            ']\n'
        ).format(**locals())

        return math_load + func_code


class LibraryObject:
    """
    Represents a whole library.
    """
    def __init__(self, info):
        self.name = info['name']
        self.path = info.get('path', '')
        if not self.path:
            self.path = Path('.').abspath()

        self.files = info.get('files', [])
        self.flags = info.get('flags', '')
        self.functions = [FunctionObject.from_obj(f) for f in info['functions']]
        self.libraries = info.get('libraries', [])
        self.lib_paths = info.get('lib_paths', [])
        self.lib_paths = [p.format(current=self.path) for p in self.lib_paths]
        self.include_paths = info.get('include_paths', [])
        self.include_paths = [p.format(current=self.path) for p in self.include_paths]

    def __eq__(self, other):
        return (self.name == other.name and
                self.path == other.path and
                self.flags == other.flags and
                self.functions == other.functions)

    def __repr__(self):
        return 'LibraryObject(%r)' % {
            'name': self.name,
            'path': self.path,
            'flags': self.flags,
            'functions': self.functions
        }

    @classmethod
    def from_file(cls, file, include_paths=None, libraries=None, lib_paths=None, flags=''):
        """
        Returns a LibraryObject based on the given filename
        """
        path = Path(file).abspath().parent
        with open(file) as fp:
            d = json.load(fp)
        d.setdefault('path', path)

        basename = Path(file).basename().replace('.json', '')
        d.setdefault('name', basename)
        d.setdefault('flags', '')
        if flags:
            d['flags'] += ' ' + flags
        d.setdefault('libraries', [])
        d.setdefault('lib_paths', [])
        d.setdefault('include_paths', [])
        d['libraries'] += libraries or []
        d['lib_paths'] += lib_paths or []
        d['include_paths'] += include_paths or []
        return LibraryObject(d)

    def to_cstr(self):
        """
        Returns the complete C code for interfacing with the library.
        """
        code = (
            '#include <stdlib.h>\n'
            '#include <stdio.h>\n'
            '#include "WolframLibrary.h"\n'
            'DLLEXPORT mint WolframLibrary_getVersion() {return WolframLibraryVersion;}\n'
            'DLLEXPORT int WolframLibrary_initialize(WolframLibraryData libData) {return 0;}\n'
            'DLLEXPORT void WolframLibrary_uninitialize(WolframLibraryData libData) {return;}\n'
        )
        for func in self.functions:
            code += func.prototype_cstr()
            code += func.func_str('    ', 'Gen')

        return code

    def to_mathstr(self, libname):
        """
        Returns the complete Mathematica code for interfacing with the library.
        """
        code = 'Needs["Developer`"];\n' + ''.join(
            func.math_str(libname, '    ', 'Gen') for func in self.functions
        )
        return code

    def generate_c_library(self, c_output, math_exec='math -script ', flags=''):
        """
        Generates the C bindings
        """
        with open(c_output, 'w') as fp:
            fp.write(self.to_cstr())

    def build_c_library(self, form_output, compiler='gcc'):
        libname = self.path.joinpath(form_output.format(name=self.name))
        gen_path = str(self.path.joinpath(self.name + 'Gen.c'))

        with open(str(self.path.joinpath(gen_path)), 'w') as fp:
            fp.write(self.to_cstr())

        compiler_type = Compiler.by_name(compiler)
        comp = compiler_type(flags=self.flags,
                             include_paths=self.include_paths,
                             libs=self.libraries,
                             lib_paths=self.lib_paths
                             )
        files = [str(self.path.joinpath(file)) for file in self.files]
        comp.compile_shared_library(files + [gen_path], libname)

        with open(str(self.path.joinpath(self.name + '.m')), 'w') as fp:
            fp.write(self.to_mathstr(libname))