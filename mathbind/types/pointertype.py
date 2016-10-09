#!/usr/bin/env python3

from mathbind.types import BasicType, BasicValueType


class PointerType(BasicType):
    """
    Represents a pointer object.
    Attributes:
    - basetype (BasicValueType): base type of the pointer.
    - const (bool): is it constant?
    """

    templates = {
        'retrieve_cstr_const': (
            '{tab}{basetype_c_name} {argname} = MArgument_get{basetype_math_name}(Args{suffix}[{index}]);\n'
        ),
        'retrieve_cstr_no_const': (
            '{tab}MTensor mtensor_{argname}{suffix} = MArgument_getMTensor(Args{suffix}[{index}]);\n'
            '{tab}{basetype_c_math_name} * data_{argname}{suffix} = libData{suffix}->MTensor_get{basetype_math_name}Data(mtensor_{argname}{suffix});\n'
            '{tab}{basetype_c_name} {argname} = * data_{argname}{suffix};\n'
        ),
        'before_mathstr': (
            '{tab}{argname}{suffix} = Developer`ToPackedArray[{{{convert_f}[{argname}]}}];\n'
        ),
        'after_mathstr': (
            '{tab}{argname}{suffix} = {argname}{suffix}[[1]];\n'
        ),
        'after_cstr': (
            '{tab}* data_{argname}{suffix} = {argname};\n'
            '{tab}libData{suffix}->MTensor_disownAll(mtensor_{argname}{suffix});\n'
        )
    }
    def __init__(self, basetype, const=False):
        self.typename = basetype.typename + ' * '
        if const:
            self.typename = 'const ' + self.typename
        self.basetype = basetype
        self.const = const

    @classmethod
    def from_str(self, s):
        """
        Tries to build a new PointerType from the string specification, failing if
        the type is value or array-like.
        """
        if s.count('*') != 1:
            raise ValueError('Not a valid pointer type')

        s = s.replace('*', '')
        before_const, _, after_const = s.partition('const')

        if not after_const:
            return PointerType(BasicValueType.from_str(before_const), False)

        return PointerType(BasicValueType.from_str(after_const), True)

    @classmethod
    def from_prototype_cstr(cls, s):
        if s.count('*') != 1:
            raise ValueError('Only single pointers are supported currently.')

        try:
            i = s.index('*')
        except (IndexError, ValueError):
            raise ValueError('no * found')

        words, _, argname = s.partition('*')

        if not words or not argname:
            raise ValueError('Not a valid pointer type')

        return PointerType.from_str(words + ' * '), argname.strip()

    @property
    def should_return(self):
        return not self.const

    @property
    def math_name(self):
        if self.const:
            return self.basetype.math_name
        else:
            base_name = self.basetype.math_name
            return '{{{0}, 1, "Shared"}}'.format(base_name)

    def __eq__(self, other):
        return self.basetype == other.basetype and self.const == other.const

    def __repr__(self):
        return 'PointerType(basetype=%r, const=%r)' % (self.basetype, self.const)

    def before_mathstr(self, argname, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix
        if self.const:
            return super().before_mathstr(argname, tab, suffix)
        convert_f = self.basetype.math_convert_f
        return self.templates['before_mathstr'].format(**locals())

    def after_mathstr(self, argname, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix
        if self.const:
            return super().after_mathstr(argname, tab, suffix)
        return self.templates['after_mathstr'].format(**locals())

    def retrieve_cstr(self, argname, index, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix

        basetype_c_name = self.basetype.c_name
        basetype_math_name = self.basetype.math_name
        basetype_c_math_name = self.basetype.c_math_name

        if self.const:
            template_name = 'retrieve_cstr_const'
        else:
            template_name = 'retrieve_cstr_no_const'

        cstr = self.templates[template_name].format(**locals())

        return cstr

    def pass_cstr(self, argname, suffix=''):
        return '&' + argname + suffix

    def prototype_cstr(self, argname):
        return self.basetype.c_name + ' * ' + argname

    def after_cstr(self, argname, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix
        if self.const:
            return ''

        convert = PointerType.templates['after_cstr']
        return convert.format(argname=argname, tab=tab, suffix=suffix)