#!/usr/bin/env python3

import unittest
from mathbind.types import BasicValueType, VoidType, PointerType
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

        name = 'myfunc'
        return_type = VoidType.from_str('void')
        arg1name = 'web'
        arg1 = PointerType.from_str('const double *')

        func = FunctionObject(name, return_type, [arg1name], [arg1])
        func2 = FunctionObject.from_str('void myfunc(const double * web);')
        self.assertEqual(func2, func)

    def test_math_load(self):
        f1 = FunctionObject.from_str('int myfunc(double arg);')
        s = 'myFuncSuf = LibraryFunctionLoad["trololo", "math_myfuncSuf", {Real}, Integer]'
        self.assertEqual(f1.mathload('trololo', 'Suf'), s)
