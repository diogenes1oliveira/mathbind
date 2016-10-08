#!/usr/bin/env python

from mathbind.compilers.compiler import Compiler


class GFortranCompiler(Compiler):
    """
    Crude interface to the gfortran compiler
    """
    name = 'gfortran'