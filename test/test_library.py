#!/usr/bin/env python3

import unittest
from mathbind.types import BasicValueType, VoidType
from mathbind.library import FunctionObject


class TestFunctionObject(unittest.TestCase):
    def test_func_str(self):
        name = 'foo'
        return_type = VoidType.from_str('void')
        arg1name = 'num'
        arg1 = BasicValueType.from_str('int')
        supposed = (
            'DLLEXPORT int math_fooGen(WolframLibraryData libDataGen, mint ArgcGen, MArgument *ArgsGen, MArgument ResGen) {\n'
            '    int num = MArgument_getInteger(ArgsGen[0]);\n'
            '    foo(num);\n'
            '    return LIBRARY_NO_ERROR;\n'
            '}')
        func = FunctionObject(name, return_type, [arg1name], [arg1])
        self.assertEqual(func.func_str('    ', 'Gen'), supposed)

    def test_prototype_cstr(self):
        name = 'foo'
        return_type = BasicValueType.from_str('double')
        arg1name = 'num'
        arg1 = BasicValueType.from_str('int')

        func = FunctionObject(name, return_type, [arg1name], [arg1])
        self.assertEqual(func.prototype_cstr(), 'double foo(int num);\n')

    def test_from_str(self):
        name = 'spiderman'
        return_type = BasicValueType.from_str('int')
        arg1name = 'web'
        arg1 = BasicValueType.from_str('double')

        func = FunctionObject(name, return_type, [arg1name], [arg1])
        self.assertEqual(FunctionObject.from_str('int spiderman(double web);'), func)