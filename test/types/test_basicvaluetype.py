#!/usr/bin/env python3

import unittest
from mathbind.types import BasicValueType


class TestBasicValueType(unittest.TestCase):
    def test_init_error(self):
        with self.assertRaises(ValueError): BasicValueType('intt')
        with self.assertRaises(ValueError): BasicValueType('longlong')
        with self.assertRaises(ValueError): BasicValueType('long uns')
        with self.assertRaises(ValueError): BasicValueType('long unsigned int3')
        with self.assertRaises(ValueError): BasicValueType('unsignedl')
        with self.assertRaises(ValueError): BasicValueType('')

    def test_init_c_math_name(self):
        self.assertEqual(BasicValueType('int').c_math_name, 'mint')
        self.assertEqual(BasicValueType('unsigned int').c_math_name, 'mint')
        self.assertEqual(BasicValueType('long long').c_math_name, 'mint')
        self.assertEqual(BasicValueType('char').c_math_name, 'mint')
        self.assertEqual(BasicValueType('long').c_math_name, 'mint')

        self.assertEqual(BasicValueType('bool').c_math_name, 'mbool')
        self.assertEqual(BasicValueType('double').c_math_name, 'mreal')

    def test_init_math_name(self):
        self.assertEqual(BasicValueType('int').math_name, 'Integer')
        self.assertEqual(BasicValueType('unsigned int').math_name, 'Integer')
        self.assertEqual(BasicValueType('long long').math_name, 'Integer')
        self.assertEqual(BasicValueType('char').math_name, 'Integer')
        self.assertEqual(BasicValueType('long').math_name, 'Integer')

        self.assertEqual(BasicValueType('bool').math_name, 'Boolean')
        self.assertEqual(BasicValueType('double').math_name, 'Real')

    def test_should_return(self):
        self.assertEqual(BasicValueType('double').should_return, False)
        self.assertEqual(BasicValueType('int').should_return, False)
        self.assertEqual(BasicValueType('bool').should_return, False)
        self.assertEqual(BasicValueType('float').should_return, False)
        self.assertEqual(BasicValueType('long long').should_return, False)

    def test_from_str(self):
        self.assertEqual(BasicValueType.from_str('bool'), BasicValueType('bool'))
        self.assertEqual(BasicValueType.from_str('long     long '), BasicValueType('long long'))
        with self.assertRaises(ValueError):
            BasicValueType.from_str('int *')

        self.assertEqual(BasicValueType.from_str('int'),
                         BasicValueType.from_str('int    '))
        self.assertEqual(BasicValueType.from_str('int'),
                         BasicValueType.from_str('   int   '))

        self.assertEqual(BasicValueType.from_str('long int'),
                         BasicValueType.from_str(' long  int   '))
        self.assertEqual(BasicValueType.from_str('long int'),
                         BasicValueType.from_str(' long   int   '))

    def test_from_prototype_cstr(self):
        BasicValueType.from_prototype_cstr('bool flag')
        BasicValueType.from_prototype_cstr('int flag_3')
        BasicValueType.from_prototype_cstr('float _3')

        with self.assertRaises(ValueError): BasicValueType.from_prototype_cstr('bool flag *')
        with self.assertRaises(ValueError): BasicValueType.from_prototype_cstr('int flag []')

        self.assertEqual(BasicValueType.from_prototype_cstr('bool flag'),
                         (BasicValueType.from_str('bool'), 'flag'))

    def test_retrieve_cstr(self):
        int_t = BasicValueType.from_str('int')
        self.assertEqual(int_t.retrieve_cstr('num', 1, suffix=''), 'int num = MArgument_getInteger(Args[1]);\n')

        int_t = BasicValueType.from_str('int')
        self.assertEqual(int_t.retrieve_cstr('num', 1, suffix='Gen'), 'int num = MArgument_getInteger(ArgsGen[1]);\n')

        int_t = BasicValueType.from_str('long long')
        self.assertEqual(int_t.retrieve_cstr('num', 1, suffix=''), 'long long num = MArgument_getInteger(Args[1]);\n')

    def test_return_cstr(self):
        long_t = BasicValueType.from_str('long long')
        func_call = 'trololo()'
        s = (
            ' long long return_valueGen3 = trololo();\n'
            ' MArgument_setInteger(ResGen3, return_valueGen3);\n'
        )
        self.assertEqual(long_t.return_cstr(func_call, tab=' ', suffix='Gen3'), s)

        float_t = BasicValueType.from_str('double')
        func_call = 'trolosdflo()'
        s = (
            ' double return_valueCap = trolosdflo();\n'
            ' MArgument_setReal(ResCap, return_valueCap);\n'
        )
        self.assertEqual(float_t.return_cstr(func_call, tab=' ', suffix='Cap'), s)

    def test_prototype(self):
        self.assertEqual(BasicValueType.from_str('bool').prototype_cstr('flag'),
                         'int flag')
        self.assertEqual(BasicValueType.from_str('float').prototype_cstr('num'),
                         'float num')