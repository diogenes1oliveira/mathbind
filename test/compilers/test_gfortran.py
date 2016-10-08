#!/usr/bin/env python3

import os
import unittest
from unittest import mock

from mathbind.compilers.gfortran import GFortranCompiler


class TestGFortranCompiler(unittest.TestCase):
    def setUp(self):
        self.os_system_backup = os.system

    def tearDown(self):
        os.system = self.os_system_backup

    def test1(self):
        os.system = mock.MagicMock(return_value=0)
        c1 = GFortranCompiler()
        c1.compile_shared_library(['file.c'], 'libfile.so')
        os.system.assert_called_with(('gfortran -fPIC -shared -o "libfile.so" "file.c"'))

    def test2(self):
        os.system = mock.MagicMock(return_value=0)
        c1 = GFortranCompiler(libs=['m', 'mock'], lib_paths=['/dev/zero'])
        c1.compile_shared_library(['file.c', 'otherfile.f90'], 'libfile.so')
        os.system.assert_called_with(('gfortran -fPIC -shared -o "libfile.so" "file.c" "otherfile.f90" -lm -lmock -L "/dev/zero"'))