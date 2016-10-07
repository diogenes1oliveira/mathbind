#!/usr/bin/env python3

import unittest
from mathbind.types import PointerType, BasicValueType


class TestPointerType(unittest.TestCase):
    def test_from_str_error(self):
        with self.assertRaises(ValueError): PointerType.from_str('int[]')
        with self.assertRaises(ValueError): PointerType.from_str('int')
        with self.assertRaises(ValueError): PointerType.from_str('unsigned long int')
        with self.assertRaises(ValueError): PointerType.from_str('unsigned long isnt *')
        with self.assertRaises(ValueError): PointerType.from_str('int **')

    def test_from_str(self):
        self.assertEqual(PointerType.from_str('int *'), PointerType(BasicValueType('int'), False))
        self.assertEqual(PointerType.from_str('double *'), PointerType(BasicValueType('double'), False))
        self.assertEqual(PointerType.from_str('const int *'), PointerType(BasicValueType('int'), True))

    def test_from_prototype_cstr(self):
        PointerType.from_prototype_cstr('int * num')
        PointerType.from_prototype_cstr('const float * _3')
        PointerType.from_prototype_cstr('double * _3')

        with self.assertRaises(ValueError): PointerType.from_prototype_cstr('bool flag []')
        with self.assertRaises(ValueError): PointerType.from_prototype_cstr('int flag ')

        self.assertEqual(PointerType.from_prototype_cstr(' int * counter '),
                         (PointerType.from_str('int *'), 'counter'))
        self.assertEqual(PointerType.from_prototype_cstr(' const int * counter '),
                         (PointerType.from_str('const int *'), 'counter'))

    def test_const(self):
        self.assertEqual(PointerType.from_str('const int *').const, True)
        self.assertEqual(PointerType.from_str('int *').const, False)

    def test_retrieve_cstr(self):
        double_t = PointerType.from_str('const double *')
        self.assertEqual(double_t.retrieve_cstr('num', 0, suffix=''), 'double num = MArgument_getReal(Args[0]);\n')

        double_t = PointerType.from_str('const double *')
        self.assertEqual(double_t.retrieve_cstr('num', 0, suffix='Wan'),
                         'double num = MArgument_getReal(ArgsWan[0]);\n')

        const_bool_t = PointerType.from_str('const bool *')
        self.assertEqual(const_bool_t.retrieve_cstr('num', 10, suffix=''),
                         'int num = MArgument_getBoolean(Args[10]);\n')

        int_t = PointerType.from_str('int *')
        self.assertEqual(int_t.retrieve_cstr('num', 10, suffix='Vis'),
                         'MTensor mtensor_numVis = MArgument_getMTensor(ArgsVis[10]);\n' +
                         'int num = * (libDataVis->MTensor_getIntegerData(mtensor_numVis));\n')

        bool_t = PointerType.from_str('bool *')
        self.assertEqual(bool_t.retrieve_cstr('flag', 10, suffix='Fal'),
                         'MTensor mtensor_flagFal = MArgument_getMTensor(ArgsFal[10]);\n' +
                         'int flag = * (libDataFal->MTensor_getBooleanData(mtensor_flagFal));\n')

    def test_pass_cstr(self):
        const_long_t = PointerType.from_str('const long *')
        self.assertEqual(const_long_t.pass_cstr('_arg'), '&_arg')

        bool_t = PointerType.from_str('const bool *')
        self.assertEqual(bool_t.pass_cstr('num'), '&num')

        long_t = PointerType.from_str('long *')
        self.assertEqual(long_t.pass_cstr('num'), '&num')