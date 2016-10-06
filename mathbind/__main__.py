#!/usr/bin/env python3

"""
Usage:
    mathbind [--def-file=<JSON_FILE>] [--output=<FILE>]
    mathbind -h | --help | --version

Options:
    -d --def-file=<JSON_FILE>     Index of the joystick to be used
    -o --output=<FILE>            JSON file with the mappings to be used
"""

import sys
import json
import opster
from mathbind.library import LibraryObject


@opster.command()
def main_command(output,
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


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    main_command.command()

if __name__ == '__main__':
    main()
