#!/usr/bin/env python3

import unittest
from mathbind.compilers.compiler import Compiler
from mathbind.compilers.gfortran import GFortranCompiler


class TestCompiler(unittest.TestCase):
    def test_find(self):
        self.assertEqual(Compiler.by_name('gfortran'), GFortranCompiler)


if __name__ == '__main__':
    unittest.main()