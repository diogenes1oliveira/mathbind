#!/usr/bin/env python3

from mathbind.types import BasicType


class BasicValueType(BasicType):
    """
    Represents a basic pure type that can be passed by value, thus excluding arrays and pointers.
    Attributes:
    - typename (str): basic C typename (int, long long, unsigned, bool, etc)
    - c_math_name (str): corresponding Mathematica C type
    - math_name (str): corresponding Mathematica type (Integer, Real)
    - c_name (str): corresponding C type (int, long long, float).
    """

    def __init__(self, typename):

        self.typename = typename

        type_parts = set(typename.split())
        self.c_name = typename

        if not type_parts:
            raise ValueError
        elif {'float', 'double'} & type_parts:
            self.c_math_name = 'mreal'
            self.math_name = 'Real'
        elif 'bool' in type_parts:
            self.c_name = 'int'
            self.c_math_name = 'mbool'
            self.math_name = 'Boolean'
        elif not type_parts - {'signed', 'unsigned', 'char', 'int', 'short', 'long'}:
            self.c_math_name = 'mint'
            self.math_name = 'Integer'
        else:
            raise ValueError('Unrecognized C type')

    @classmethod
    def from_str(cls, s):
        """
        Tries to build a new BasicValueType from the string specification, failing if
        the type is a pointer or array-like.
        """
        if '*' in s or '[' in s or ']' in s:
            raise ValueError('Not a valid basic C type')

        while '  ' in s:
            s = s.replace('  ', ' ')

        return BasicValueType(s.strip())

    @classmethod
    def from_prototype_cstr(cls, s):
        """
        Tries to extract (type, argname) from the string.
        """
        while s.count('  ') > 2:
            s = s.replace('  ', '')
        s = s.strip()

        if not s.replace(' ', '').replace('_', '').isalnum():
            raise ValueError('Unrecognized characters')

        *words, argname = s.split()
        return BasicValueType.from_str(' '.join(words)), argname.strip()

    def __repr__(self):
        return 'BasicValueType(typename=%r)' % self.typename

    def __eq__(self, other):
        return self.typename == other.typename

    def retrieve_cstr(self, argname, index, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix
        form = '{tab}{self.c_name} {argname} = MArgument_get{self.math_name}(Args{suffix}[{index}]);\n'
        return form.format(argname=argname, self=self, tab=tab, index=index, suffix=suffix)

    def return_cstr(self, func_call, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix
        form = (
            '{tab}{self.c_name} return_value{suffix} = {func_call};\n'
            '{tab}MArgument_set{self.math_name}(Res{suffix}, return_value{suffix});\n'
        )
        return form.format(func_call=func_call, tab=tab, self=self, suffix=suffix)

    def prototype_cstr(self, argname):
        return self.c_name + ' ' + argname

    def prototype_return_cstr(self):
        """
        Returns a C string representing the declaration in a prototype return.
        """
        return self.c_name

    @property
    def math_convert_f(self):
        """
        Returns the Mathematica function responsible for converting values
        to this one.
        """
        if 'float' in self.typename or 'double' in self.typename:
            return 'N'
        else:
            return 'IntegerPart'