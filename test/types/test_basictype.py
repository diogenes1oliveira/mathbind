#!/usr/bin/env python3

import unittest
from mathbind.types import BasicType


class TestBasicType(unittest.TestCase):
    def test_before_mathstr(self):
        d1 = {'argname': 'myArg', 'suffix': 'Gen', 'tab': '\t\t'}
        int_t = BasicType.from_str('int')
        self.assertEqual(int_t.before_mathstr(**d1),
                         int_t.templates['before_mathstr'].format(**d1))