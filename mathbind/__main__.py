#!/usr/bin/env python3

import sys
import json
import opster
from path import Path
import mathbind
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

@opster.command(usage='[-m MATH_EXECUTABLE] [-f FLAGS] def_file [-L PATH1;PATH2] [-l lib1;lib2] [-I inc1;inc2]')
def build_c(def_file,
            flags=('f', '', 'Compiler flags'),
            lib_paths=('L', '', 'Library paths'),
            libraries=('l', '', 'Libraries to link'),
            include_paths=('I', '', 'Include paths')):
    """
    Generates and builds the boilerplate code to connect Mathematica to arbitrary external libraries.
    """
    lib_paths = lib_paths.split(';') if lib_paths else ''
    libraries = libraries.split(';') if libraries else ''
    include_paths = include_paths.split(';') if include_paths else ''
    lib = LibraryObject.from_file(def_file, include_paths, libraries, lib_paths, flags)

    lib.build_c_library('lib{name}.so')


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
