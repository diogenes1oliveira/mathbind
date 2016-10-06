#!/usr/bin/env python3

import sys
import json
import opster
from mathbind.library import LibraryObject


@opster.command(usage='[-d FILE] [-o FILE]')
def main_command(output=('o','','Output file, defaults to stdout'),
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
