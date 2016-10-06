#!/usr/bin/env python3

import unittest
from mathbind.types import VoidType


class TestVoidType(unittest.TestCase):
    def test_init_error(self):
        with self.assertRaises(ValueError): VoidType('intt')
        with self.assertRaises(ValueError): VoidType('longlong')
        with self.assertRaises(ValueError): VoidType('long uns')
        with self.assertRaises(ValueError): VoidType('long unsigned int3')
        with self.assertRaises(ValueError): VoidType('unsignedl')
        with self.assertRaises(ValueError): VoidType('')

        with self.assertRaises(ValueError): VoidType('int')
        with self.assertRaises(ValueError): VoidType('long long')
        with self.assertRaises(ValueError): VoidType('const double *')
        with self.assertRaises(ValueError): VoidType('double []')
        with self.assertRaises(ValueError): VoidType('int [30]')

        with self.assertRaises(ValueError): VoidType('  void  ')
        VoidType('void')

    def test_from_str(self):
        with self.assertRaises(ValueError): VoidType.from_str(' void 2')
        VoidType.from_str('void')
        VoidType.from_str('   void   ')

    def test_return_cstr(self):
        func_call = 'f(&a, b, c)'
        r = VoidType.from_str('void').return_cstr(func_call, ' ', '')
        self.assertEqual(r, ' f(&a, b, c);\n')