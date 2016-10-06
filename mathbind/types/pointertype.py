#!/usr/bin/env python3

from mathbind.types import BasicType, BasicValueType


class PointerType(BasicType):
    """
    Represents a pointer object.
    Attributes:
    - basetype (BasicValueType): base type of the pointer.
    - const (bool): is it constant?
    """

    def __init__(self, basetype, const=False):
        self.typename = basetype.typename + ' * '
        self.basetype = basetype
        self.const = const

    @classmethod
    def from_str(self, s):
        """
        Tries to build a new PointerType from the string specification, failing if
        the type is value or array-like.
        """
        if s.count('*') != 1:
            raise ValueError

        s = s.replace('*', '')
        before_const, _, after_const = s.partition('const')

        if not after_const:
            return PointerType(BasicValueType.from_str(before_const), False)

        return PointerType(BasicValueType.from_str(after_const), True)

    @classmethod
    def from_prototype_cstr(cls, s):
        if s.count('*') != 1:
            raise ValueError('only single pointers are supported currently.')

        try:
            i = s.index('*')
        except (IndexError, ValueError):
            raise ValueError('no * found')

        words, _, argname = s.partition('*')

        if not words or not argname:
            raise ValueError('invalid pointer argument')

        return PointerType.from_str(words + ' * '), argname.strip()

    def __eq__(self, other):
        return self.basetype == other.basetype and self.const == other.const

    def __repr__(self):
        return 'PointerType(basetype=%r, const=%r)' % (self.basetype, self.const)

    def retrieve_cstr(self, argname, index, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix
        if self.const:
            form = '{tab}{self.basetype.c_name} {argname} = MArgument_get{self.basetype.math_name}(Args{suffix}[{index}]);\n'
        else:
            form = ('{tab}MTensor mtensor_{argname}{suffix} = MArgument_getMTensor(Args{suffix}[{index}]);\n'
                    '{tab}{self.basetype.c_name} {argname} = * (libData{suffix}->MTensor_get{self.basetype.math_name}Data(mtensor_{argname}{suffix}));\n')

        return form.format(argname=argname, self=self, tab=tab, index=index, suffix=suffix)

    def pass_cstr(self, argname, suffix=''):
        return '&' + argname + suffix

    def prototype_cstr(self, argname):
        return self.basetype.c_name + ' * ' + argname

    def after_cstr(self, argname, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix
        if self.const:
            return ''

        convert = (
            '{tab}libData{suffix}->MTensor_disownAll(mtensor_{argname}{suffix});\n'
        )
        return convert.format(argname=argname, self=self, tab=tab, suffix=suffix)