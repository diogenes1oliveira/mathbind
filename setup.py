#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  File based on https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mathbind',

    version='0.0.1',

    description='',
    long_description=long_description,

    url='https://github.com/diogenes1oliveira/mathbind',

    author='Diógenes Oliveira',
    author_email='diogenes1oliveira@gmail.com',

    # Choose your license
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],

    # What does your project relate to?
    keywords='python python3 mathematica linking',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=[]),

    install_requires=['opster', 'path.py'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'mathbind = mathbind.__main__:main',
        ],
    },
)
