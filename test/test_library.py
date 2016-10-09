#!/usr/bin/env python3

import tempfile
import unittest
from path import Path
from mathbind.types import BasicValueType, VoidType, PointerType, ArrayType
from mathbind.library import FunctionObject, LibraryObject


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
        s1 = 'myfuncSuf = LibraryFunctionLoad["trololo", "math_myfuncSuf", {Real}, Integer];\n'
        self.assertEqual(f1.math_load('trololo', 'Suf'), s1)

        f2 = FunctionObject.from_str('void spiderman(int arg);')
        s2 = 'spidermanGeni = LibraryFunctionLoad["trololo", "math_spidermanGeni", {Integer}, "Void"];\n'
        self.assertEqual(f2.math_load('trololo', 'Geni'), s2)

        f3 = FunctionObject.from_str('double func1(const int * var);')
        s3 = 'func1Foo = LibraryFunctionLoad["trololo", "math_func1Foo", {Integer}, Real];\n'
        self.assertEqual(f3.math_load('trololo', 'Foo'), s3)

        f4 = FunctionObject.from_str('double func1(float * var);')
        s4 = 'func1Foo = LibraryFunctionLoad["trololo", "math_func1Foo", {{Real, 1, "Shared"}}, Real];\n'
        self.assertEqual(f4.math_load('trololo', 'Foo'), s4)

    def test1_math_str(self):
        f1 = FunctionObject.from_str('int myfunc(double arg);')
        s1 = f1.math_load('trololo', 'Gen') + (
            'myfunc[arg_] := Module[{returnGen, argGen},\n'
            '\targGen = arg;\n'
            '\treturnGen = myfuncGen[argGen];\n'
            '\t{returnGen}\n'
            ']\n'
        )
        self.assertEqual(f1.math_str('trololo', '\t', 'Gen'), s1)

    def test2_math_str(self):
        f2 = FunctionObject.from_str('int myfunc(const double * arg);')
        s2 = f2.math_load('trololo', 'Gen') + (
            'myfunc[arg_] := Module[{returnGen, argGen},\n'
            '\targGen = arg;\n'
            '\treturnGen = myfuncGen[argGen];\n'
            '\t{returnGen}\n'
            ']\n'
        )
        self.assertEqual(f2.math_str('trololo', '\t', 'Gen'), s2)

    def test3_math_str(self):
        f3 = FunctionObject.from_str('int myfunc(const double * arg, int size);')
        s3 = f3.math_load('trololo', 'Gen') + (
            'myfunc[arg_, size_] := Module[{returnGen, argGen, sizeGen},\n'
            '\targGen = arg;\n'
            '\tsizeGen = size;\n'
            '\treturnGen = myfuncGen[argGen, sizeGen];\n'
            '\t{returnGen}\n'
            ']\n'
        )
        self.assertEqual(f3.math_str('trololo', '\t', 'Gen'), s3)

    def test4_math_str(self):
        f4 = FunctionObject.from_str('void myfunc(double * arg);')
        s4 = f4.math_load('trololo', 'Gen') + (
            'myfunc[arg_] := Module[{returnGen, argGen},\n' +
            PointerType.from_str('double *').before_mathstr('arg', '\t', 'Gen') +
            '\treturnGen = myfuncGen[argGen];\n'
            '\t{argGen}\n'
            ']\n'
        )
        self.assertEqual(f4.math_str('trololo', '\t', 'Gen'), s4)

    def test5_math_str(self):
        f5 = FunctionObject.from_str('void myfunc(double arg[3]);')
        s5 = f5.math_load('trololo', 'Gen') + (
            'myfunc[arg_] := Module[{returnGen, argGen},\n' +
            ArrayType.from_str('double [3]').before_mathstr('arg', '\t', 'Gen') +
            '\treturnGen = myfuncGen[argGen];\n'
            '\t{argGen}\n'
            ']\n'
        )
        self.assertEqual(f5.math_str('trololo', '\t', 'Gen'), s5)

    def test6_math_str(self):
        f6 = FunctionObject.from_str('void myfunc_(double arg[3]);')
        s6 = f6.math_load('trololo', 'Gen') + (
            'myfunc[arg_] := Module[{returnGen, argGen},\n' +
            ArrayType.from_str('double [3]').before_mathstr('arg', '\t', 'Gen') +
            '\treturnGen = myfuncGen[argGen];\n'
            '\t{argGen}\n'
            ']\n'
        )
        self.assertEqual(f6.math_str('trololo', '\t', 'Gen'), s6)


class TestLibraryObject(unittest.TestCase):
    def setUp(self):
        double_t = BasicValueType.from_str('double')
        void_t = VoidType.from_str('void')
        f1 = FunctionObject('myfunc', void_t, ['arg1'], [double_t])
        self.lib1 = LibraryObject({
            "name": "mylib",
            "functions": [f1]
        })

        self.temp1 = Path(tempfile.mkdtemp())
        self.file2 = self.temp1.joinpath('def2.json')
        int_t = BasicValueType.from_str('int')
        f2 = FunctionObject('foo', int_t, ['bar'], [double_t])
        self.lib2 = LibraryObject({
            'name': 'def2',
            'path': self.temp1,
            'flags': '',
            'functions': [f2]

        })
        with open(self.file2, 'w') as fp:
            fp.write('''
            {
                "functions": [
                    "int foo(double bar);"
                ]
            }
            ''')

    def tearDown(self):
        self.temp1.rmtree()

    def test_properties(self):
        lib2 = LibraryObject.from_file(self.file2)
        self.assertEqual(lib2, self.lib2)



    def test_to_mathstr(self):
        s1 = 'Needs["Developer`"];\n'
        f1 = FunctionObject.from_str('void myfunc(double arg1);')

        self.assertEqual(self.lib1.to_mathstr("mylibdll"),
                         s1 + f1.math_str('mylibdll', '    ', 'Gen'))