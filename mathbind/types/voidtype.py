#!/usr/bin/env python3

from mathbind.types import BasicType


class VoidType(BasicType):
    """
    Represents the void type, used in the return type of functions.
    """
    def __init__(self, typename):
        if typename != 'void':
            raise ValueError("VoidType only accepts the type specification 'void'")
        self.typename = 'void'

    def __eq__(self, other):
        return self.typename == other.typename

    def __repr__(self):
        return 'VoidType(%r)' % 'void'

    @property
    def math_name(self):
        return '"Void"'
    
    @classmethod
    def from_str(self, s):
        """
        Tries to build a new VoidType from the string specification, failing if
        the type is not 'void'.
        """
        return VoidType(s.strip())

    def retrieve_cstr(self, argname, index, tab='', suffix=None):
        """
        Because the void type can not be passed as an argument, this method is
        left unimplemented.
        """
        raise NotImplemented

    def return_cstr(self, func_call, tab='', suffix=None):
        return '{tab}{func_call};\n'.format(func_call=func_call, tab=tab)

    def prototype_return_cstr(self):
        """
        Returns a C string representing the declaration in a prototype return.
        """
        return 'void'