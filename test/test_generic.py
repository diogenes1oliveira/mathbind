#!/usr/bin/env python3

import tempfile
import unittest
from path import Path
from mathbind.generic import iterate_folder


class TestIterateFolder(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        self.dir.rmtree()

    def test1(self):
        filenames = ['nada.py', '__init__.py', 'saida.jpeg', 'nada.txt']
        filepaths = [self.dir.joinpath(f) for f in filenames]
        for f in filenames:
            open(self.dir.joinpath(f), 'w').close()

        f1 = self.dir.joinpath('nada.py')
        self.assertListEqual(sorted(list(iterate_folder(f1, '*.py'))),
                             sorted(filepaths[:2]))
        self.assertListEqual(sorted(list(iterate_folder(f1, '*.py', ['__init__']))),
                             sorted(filepaths[:1]))


if __name__ == '__main__':
    unittest.main()