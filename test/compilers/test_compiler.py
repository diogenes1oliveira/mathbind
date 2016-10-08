#!/usr/bin/env python3

import unittest
from mathbind.compilers.compiler import Compiler
from mathbind.compilers.gcc import GccCompiler


class TestCompiler(unittest.TestCase):
    def test_find(self):
        self.assertEqual(Compiler.by_name('gcc'), GccCompiler)


if __name__ == '__main__':
    unittest.main()