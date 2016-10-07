#!/usr/bin/env python3

import unittest
from mathbind.types import ArrayType, BasicValueType


class TestArrayType(unittest.TestCase):
    def test_from_str_error_array(self):
        with self.assertRaises(ValueError): ArrayType.from_str('int *')
        with self.assertRaises(ValueError): ArrayType.from_str('int')
        with self.assertRaises(ValueError): ArrayType.from_str('const long int *')
        with self.assertRaises(ValueError): ArrayType.from_str('double [')
        with self.assertRaises(ValueError): ArrayType.from_str('double [[ ]')
        with self.assertRaises(ValueError): ArrayType.from_str('double [[ ]]')
        with self.assertRaises(ValueError): ArrayType.from_str('double ] s [')

    def test_from_str_error_type(self):
        ArrayType.from_str('float []')
        ArrayType.from_str('int[]')
        with self.assertRaises(ValueError): ArrayType.from_str('ist [ ]')
        with self.assertRaises(ValueError): ArrayType.from_str('[ ] int')
        with self.assertRaises(ValueError): ArrayType.from_str('floating []')

    def test_from_str_const(self):
        self.assertEqual(ArrayType.from_str(' const float []').const, True)
        self.assertEqual(ArrayType.from_str(' const double [3]').const, True)
        self.assertEqual(ArrayType.from_str('const   long long int [length]').const, True)

        self.assertEqual(ArrayType.from_str(' const float []').basetype, BasicValueType.from_str('float'))
        self.assertEqual(ArrayType.from_str(' const double [3]').basetype, BasicValueType.from_str('double'))
        self.assertEqual(ArrayType.from_str('const   long long int [length]').basetype, BasicValueType.from_str('long long int'))

    def test_from_prototype_cstr(self):
        ArrayType.from_prototype_cstr('int num[]')
        ArrayType.from_prototype_cstr('float _3[30]')
        ArrayType.from_prototype_cstr('double asd[length]')

        with self.assertRaises(ValueError): ArrayType.from_prototype_cstr('int * flag ')
        with self.assertRaises(ValueError): ArrayType.from_prototype_cstr('float flag ')

        self.assertEqual(ArrayType.from_prototype_cstr(' float geni [length] '),
                         (ArrayType.from_str('float[length]'), 'geni'))
        self.assertEqual(ArrayType.from_prototype_cstr(' int counter [3] '),
                         (ArrayType.from_str('int [3]'), 'counter'))

    def test_basic_type(self):
        self.assertEqual(ArrayType.from_str('int [ ]').basetype, BasicValueType.from_str('int'))
        self.assertEqual(ArrayType.from_str('double [3]').basetype, BasicValueType.from_str('double'))
        self.assertEqual(ArrayType.from_str('float [length]').basetype, BasicValueType.from_str('float'))

    def test_policy(self):
        self.assertEqual(ArrayType.from_str('int [ ]').policy, 'infinite')
        self.assertEqual(ArrayType.from_str('double [3]').policy, 'fixed')
        self.assertEqual(ArrayType.from_str('float [length]').policy, 'variable')
        self.assertEqual(ArrayType.from_str('long long [length]').policy, 'variable')

    def test_before_cstr(self):
        int_t = ArrayType.from_str('int [3]')
        s = (
            ' /* Converting triple */\n'
            ' int * triple = (int *) data_tripleGen;\n'
            ' if(sizeof(mint) != sizeof(int)) {\n'
            '     triple = malloc(sizeof(int) * 3);\n'
            '     for(int iGen = 0; iGen < 3; ++iGen)\n'
            '         triple[iGen] = data_tripleGen[iGen];\n'
            ' }\n'
        )
        self.assertEqual(int_t.before_cstr('triple', ' ', 'Gen'), s)

        float_t = ArrayType.from_str('float [3]')
        s = (
            ' /* Converting triple */\n'
            ' float * triple = (float *) data_tripleGen2;\n'
            ' if(sizeof(mreal) != sizeof(float)) {\n'
            '     triple = malloc(sizeof(float) * 3);\n'
            '     for(int iGen2 = 0; iGen2 < 3; ++iGen2)\n'
            '         triple[iGen2] = data_tripleGen[iGen2];\n'
            ' }\n'
        )
        self.assertEqual(float_t.before_cstr('triple', ' ', 'Gen2'), s)

        long_t = ArrayType.from_str('long [length]')
        s = (
            ' /* Converting triple */\n'
            ' long * triple = (long *) data_tripleGen;\n'
            ' if(sizeof(mint) != sizeof(long)) {\n'
            '     triple = malloc(sizeof(long) * length);\n'
            '     for(int iGen = 0; iGen < length; ++iGen)\n'
            '         triple[iGen] = data_tripleGen[iGen];\n'
            ' }\n'
        )
        self.assertEqual(long_t.before_cstr('triple', ' ', 'Gen'), s)

    def test_after_cstr(self):
        int_t = ArrayType.from_str('int [3]')
        s = (
            ' /* Copying and releasing triple */\n'
            ' if(sizeof(mint) != sizeof(int)) {\n'
            '     for(int iGen = 0; iGen < 3; ++iGen)\n'
            '         data_tripleGen[iGen] = triple[iGen];\n'
            '     free(triple);\n'
            ' }\n'
            ' libDataGen->MTensor_disownAll(mtensor_tripleGen);\n'
        )
        self.assertEqual(int_t.after_cstr('triple', ' ', 'Gen'), s)

        double_t = ArrayType.from_str('double [3]')
        s = (
            ' /* Copying and releasing triple */\n'
            ' if(sizeof(mreal) != sizeof(double)) {\n'
            '     for(int iGeni = 0; iGeni < 3; ++iGeni)\n'
            '         data_tripleGen[iGeni] = triple[iGeni];\n'
            '     free(triple);\n'
            ' }\n'
            ' libDataGeni->MTensor_disownAll(mtensor_tripleGeni);\n'
        )
        self.assertEqual(double_t.after_cstr('triple', ' ', 'Geni'), s)

    def test_retrieve_cstr(self):
        double_t = ArrayType.from_str('double [3]')
        before = double_t.before_cstr('ironman', ' ', 'Ant')
        s = (
            ' MTensor mtensor_ironmanAnt = MArgument_getMTensor(ArgsAnt[2]);\n'
            ' mreal * data_ironmanAnt = libDataAnt->MTensor_getRealData(mtensor_ironmanAnt);\n')
        self.assertEqual(double_t.retrieve_cstr('ironman', 2, ' ', 'Ant'), s + before)

    def test_const_array_before_mathstr(self):
        double_t = ArrayType.from_str('double [3]')
        s = ' varGen = Developer`ToPackedArray[Map[N, var]];\n'
        self.assertEqual(double_t.before_mathstr('var', ' ', 'Gen'), s)