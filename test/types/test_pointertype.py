#!/usr/bin/env python3

import unittest
from mathbind.types import PointerType, BasicValueType, BasicType


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

        int_t = BasicValueType.from_str('int')
        self.assertEqual(PointerType.from_prototype_cstr(' int * counter '),
                         (PointerType(int_t, False), 'counter'))
        self.assertEqual(PointerType.from_prototype_cstr(' const int * trololo '),
                         (PointerType(int_t, True), 'trololo'))
        self.assertEqual((PointerType(int_t, True), 'value'),
                         PointerType.from_prototype_cstr('  const   int * value'))

        double_t = BasicValueType.from_str('double')
        self.assertEqual((PointerType(double_t, True), 'value'),
                         PointerType.from_prototype_cstr('const double * value'))

    def test_typename(self):
        int_t = BasicValueType.from_str('int')
        double_t = BasicValueType.from_str('double')

        self.assertEqual(PointerType(int_t, True).typename, 'const int * ')
        self.assertEqual(PointerType(int_t, False).typename, 'int * ')

        self.assertEqual(PointerType(double_t, True).typename, 'const double * ')
        self.assertEqual(PointerType(double_t, False).typename, 'double * ')

    def test_const(self):
        self.assertEqual(PointerType.from_str('const int *').const, True)
        self.assertEqual(PointerType.from_str('int *').const, False)

        self.assertEqual(PointerType.from_str(' const   int *').const, True)

    def test_should_return(self):
        self.assertEqual(PointerType.from_str('const double *').should_return,
                         False)
        self.assertEqual(PointerType.from_str('int *').should_return,
                         True)
        self.assertEqual(PointerType.from_str('  long long *').should_return,
                         True)
        self.assertEqual(PointerType.from_str('const bool *').should_return,
                         False)

    def test_math_name(self):
        self.assertEqual(PointerType.from_str('const double *').math_name,
                         'Real')
        self.assertEqual(PointerType.from_str('float *').math_name,
                         '{Real, 1, "Shared"}')
        self.assertEqual(PointerType.from_str('int *').math_name,
                         '{Integer, 1, "Shared"}')
        self.assertEqual(PointerType.from_str('const long long int *').math_name,
                         'Integer')
        self.assertEqual(PointerType.from_str('const bool *').math_name,
                         'Boolean')

    def test_before_mathstr(self):
        double_t = PointerType.from_str('const double *')
        s = BasicType.templates['before_mathstr'].format(
            tab='   ', argname='myVar', suffix='Suf',
            convert_f = double_t.basetype.math_convert_f
        )
        self.assertEqual(double_t.before_mathstr('myVar', '   ', 'Suf'), s)

        int_t = PointerType.from_str('const int *')
        s = BasicType.templates['before_mathstr'].format(
            tab='\t', argname='myVar', suffix='MySuffix',
            convert_f = int_t.basetype.math_convert_f
        )
        self.assertEqual(int_t.before_mathstr('myVar', '\t', 'MySuffix'), s)

        float_t = PointerType.from_str('float *')
        s = PointerType.templates['before_mathstr'].format(
            tab='\t', argname='myVar', suffix='MySuffix',
            convert_f = float_t.basetype.math_convert_f
        )
        self.assertEqual(float_t.before_mathstr('myVar', '\t', 'MySuffix'), s)

        int_t = PointerType.from_str('int *')
        s = PointerType.templates['before_mathstr'].format(
            tab='\t', argname='myVar', suffix='MySuffix',
            convert_f=int_t.basetype.math_convert_f
        )
        self.assertEqual(int_t.before_mathstr('myVar', '\t', 'MySuffix'),
                         s)

    def test_after_mathstr(self):
        double_t = PointerType.from_str('const double *')
        self.assertEqual(double_t.after_mathstr('myVar', '   ', 'Suf'), '')

        int_t = PointerType.from_str('int *')
        s = PointerType.templates['after_mathstr'].format(
            tab='   ', argname='myVar', suffix='Suf'
        )
        self.assertEqual(double_t.after_mathstr('myVar', '   ', 'Suf'), '')

    def test_retrieve_cstr(self):
        double_t = PointerType.from_str('const double *')
        s = double_t.templates['retrieve_cstr_const'].format(
            argname='num', index=0,suffix='suff', tab='',
            basetype_c_name=double_t.basetype.c_name,
            basetype_math_name=double_t.basetype.math_name
        )
        self.assertEqual(double_t.retrieve_cstr('num', 0, suffix='suff'), s)

        s = double_t.templates['retrieve_cstr_const'].format(
            argname='argWhatever', index=10,suffix='Wan', tab='',
            basetype_c_name=double_t.basetype.c_name,
            basetype_math_name=double_t.basetype.math_name
        )
        self.assertEqual(double_t.retrieve_cstr('argWhatever', 10, suffix='Wan'),
                         s)

        const_bool_t = PointerType.from_str('const bool *')
        s = const_bool_t.templates['retrieve_cstr_const'].format(
            argname='arg', index=10,suffix='Wan', tab='',
            basetype_c_name=const_bool_t.basetype.c_name,
            basetype_math_name=const_bool_t.basetype.math_name
        )
        self.assertEqual(const_bool_t.retrieve_cstr('arg', 10, suffix='Wan'),
                         s)

        int_t = PointerType.from_str('int *')
        s = int_t.templates['retrieve_cstr_no_const'].format(
            argname='arg2', index=2,suffix='Vis', tab='',
            basetype_c_name=int_t.basetype.c_name,
            basetype_math_name=int_t.basetype.math_name,
            basetype_c_math_name=int_t.basetype.c_math_name
        )
        self.assertEqual(int_t.retrieve_cstr('arg2', 2, suffix='Vis'),
                         s)

        bool_t = PointerType.from_str('bool *')
        s = bool_t.templates['retrieve_cstr_no_const'].format(
            argname='flag', index=200,suffix='Fal', tab='',
            basetype_c_name=bool_t.basetype.c_name,
            basetype_math_name=bool_t.basetype.math_name,
            basetype_c_math_name=bool_t.basetype.c_math_name
        )
        self.assertEqual(bool_t.retrieve_cstr('flag', 200, suffix='Fal'),
                         s)

    def test_pass_cstr(self):
        const_long_t = PointerType.from_str('const long *')
        self.assertEqual(const_long_t.pass_cstr('_arg'), '&_arg')

        bool_t = PointerType.from_str('const bool *')
        self.assertEqual(bool_t.pass_cstr('num'), '&num')

        long_t = PointerType.from_str('long *')
        self.assertEqual(long_t.pass_cstr('num'), '&num')

    def test_after_cstr(self):
        const_int_t = PointerType.from_str('const int *')
        self.assertEqual(const_int_t.after_cstr('var', '\t', 'Suffix'), '')

        float_t = PointerType.from_str('float *')
        s = PointerType.templates['after_cstr'].format(
            argname='var', tab='\t', suffix='M'
        )
        self.assertEqual(float_t.after_cstr('var', '\t', 'M'), s)