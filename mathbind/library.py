#!/usr/bin/env python3

import mathbind
from mathbind.types import BasicType


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


class LibraryObject:
    """
    Represents a whole library.
    """
    def __init__(self, info):
        self.name = info['name']
        self.functions = [FunctionObject.from_obj(f) for f in info['functions']]

    def to_cstr(self):
        """
        Returns the complete code for interfacing with the library.

        :return: str
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