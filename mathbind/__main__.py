#!/usr/bin/env python3

import sys
import json
import opster
from path import Path
from mathbind.library import LibraryObject


@opster.command(usage='[-d FILE] [-o FILE]')
def generate_c(output=('o','','Output file, defaults to stdout'),
                 def_file=('d', '', 'JSON file with the definition of the library structure')):
    """
    A Python tool to auto-generate the boilerplate code to connect Mathematica to arbitrary external libraries.
    """
    fp_out = open(output, 'w') if output else sys.stdout
    fp_in = open(def_file) if def_file else sys.stdin

    lib_def = json.load(fp_in)
    lib = LibraryObject(lib_def)

    fp_out.write(lib.to_cstr())
    fp_out.close()
    fp_in.close()

@opster.command(usage='[-m MATH_EXECUTABLE] [-f FLAGS] def_file -o lib_file')
def build_c(def_file,
            lib_file,
            math_exec=('m', 'math -script ', 'Mathematica script runner'),
            flags=('f', '', 'Compiler flags')):
    """
    Generates and builds the boilerplate code to connect Mathematica to arbitrary external libraries.
    """
    lib = LibraryObject.from_file(def_file, flags)

    lib.build_c_library(lib.path.joinpath(lib_file), math_exec)


@opster.command(usage='[-d FILE] [-o FILE]')
def generate_math(libname,
                  output=('o','','Output file, defaults to stdout'),
                  def_file=('d', '', 'JSON file with the definition of the library structure')):
    """
    A Python tool to auto-generate the boilerplate code to connect Mathematica to arbitrary external libraries. This command generates the Mathematica code.
    """
    fp_out = open(output, 'w') if output else sys.stdout
    fp_in = open(def_file) if def_file else sys.stdin

    lib_def = json.load(fp_in)
    lib = LibraryObject(lib_def)

    fp_out.write(lib.to_mathstr(libname))
    fp_out.close()
    fp_in.close()


def main(argv=None):
    if argv is not None:
        sys.argv = ['mathbind'] + argv

    opster.dispatch()

if __name__ == '__main__':
    main()
