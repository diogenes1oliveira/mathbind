#!/usr/bin/env python

import os
from mathbind.compilers.compiler import Compiler


class GccCompiler(Compiler):
    """
    Crude interface to the gfortran compiler
    """
    name = 'gcc'

    def __init__(self, flags='', include_paths=None, libs=None, lib_paths=None, command='gcc'):
        self.command = command
        self.flags = flags
        self.include_paths = include_paths or []
        self.libs = libs or []
        self.lib_paths = lib_paths or []

    def compile_shared_library(self, files, output):
        include = ' '.join('-I "' + inc + '"' for inc in self.include_paths)
        lib = ' '.join('-l' + lib for lib in self.libs)
        lib_path = ' '.join('-L "' + lib + '"' for lib in self.lib_paths)
        flags = ' '.join(self.flags)

        output = '-o "' + output + '" '
        files = ' '.join('"{}"'.format(f) for f in files)
        command = self.command

        extra = ' '.join(part for part in [include, lib, lib_path, flags]
                         if part)
        if extra: extra = ' ' + extra

        form = '{command} -fPIC -shared {output}{files}'
        command = form.format(**locals()) + extra

        return os.system(command)