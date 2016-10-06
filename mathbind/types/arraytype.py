#!/usr/bin/env python3

from mathbind.types import BasicType, BasicValueType


class ArrayType(BasicType):
    """
    Represents an array type.
    Attributes:
    - basetype (BasicValueType): base type of the pointer.
    - policy (str): size policy of the array. Can be 'fixed', 'infinite', 'variable' (tied to another variable).
    - size (str or int):
    """

    def __init__(self, basetype, policy, size=None):
        self.basetype = basetype
        self.typename = basetype.typename + ' [{}]'.format('' if size is None else size)
        self.policy = policy
        self.size = size

    @classmethod
    def from_str(cls, s):
        """
        Tries to build a new ArrayType from the string specification, failing if
        the type is value or pointer-like.
        """
        bracket1 = s.index('[')
        bracket2 = s.index(']')
        if bracket1 > bracket2 or s.count('[') != 1 or s.count(']') != 1:
            raise ValueError

        type_spec = s[:bracket1].strip()
        length_spec = s[bracket1 + 1: bracket2].strip()

        size = None
        policy = 'infinite'

        try:
            size = int(length_spec)
            policy = 'fixed'
        except ValueError:
            if length_spec:
                policy = 'variable'
                size = length_spec

        return ArrayType(BasicValueType.from_str(type_spec), policy, size)

    @classmethod
    def from_prototype_cstr(cls, s):
        """
        Tries to extract (type, argname) from the string.
        """
        try:
            bra1, bra2 = s.index('['), s.index(']')
        except (IndexError, ValueError):
            raise ValueError('no brackets found')

        if bra1 > bra2:
            raise ValueError('brackets out of order')

        *words, argname = s[: bra1].split()
        return ArrayType.from_str(' '.join(words) + '[' + s[bra1 + 1:bra2] + ']'), argname

    def __eq__(self, other):
        return (self.basetype == other.basetype and self.policy == other.policy
                and self.size == other.size)

    def __repr__(self):
        return ('ArrayType(basetype=%r, policy=%r, size=%r)'
                % (self.basetype, self.policy, self.size))

    def before_cstr(self, argname, tab='', suffix=None):
        """
        Returns a C string with the instructions to convert the argname from the
        Mathematica required format.
        """
        if suffix is None:
            suffix = self.default_suffix
        convert = (
            '{tab}/* Converting {argname} */\n'
            '{tab}{self.basetype.c_name} * {argname} = ({self.basetype.c_name} *) data_{argname}{suffix};\n'
            '{tab}if(sizeof({self.basetype.c_math_name}) != sizeof({self.basetype.c_name})) {{\n'
            '{tab}    {argname} = malloc(sizeof({self.basetype.c_name}) * {self.size});\n'
            '{tab}    for(int i{suffix} = 0; i{suffix} < {self.size}; ++i{suffix})\n'
            '{tab}        {argname}[i{suffix}] = data_{argname}Gen[i{suffix}];\n'
            '{tab}}}\n'
        )
        return convert.format(argname=argname, self=self, tab=tab, suffix=suffix)

    def after_cstr(self, argname, tab='', suffix=None):
        """
        Returns a C string with the instructions to convert the argname back to the
        Mathematica required format.
        """
        if suffix is None:
            suffix = self.default_suffix
        convert = (
            '{tab}/* Copying and releasing {argname} */\n'
            '{tab}if(sizeof({self.basetype.c_math_name}) != sizeof({self.basetype.c_name})) {{\n'
            '{tab}    for(int i{suffix} = 0; i{suffix} < {self.size}; ++i{suffix})\n'
            '{tab}        data_{argname}Gen[i{suffix}] = {argname}[i{suffix}];\n'
            '{tab}    free({argname});\n'
            '{tab}}}\n'
            '{tab}libData{suffix}->MTensor_disownAll(mtensor_{argname}{suffix});\n'
        )
        return convert.format(argname=argname, self=self, tab=tab, suffix=suffix)

    def retrieve_cstr(self, argname, index, tab='', suffix=None):
        """
        Returns a C string to retrieve the argument from Mathematica.
        Args:
        - argname (str): name of the argument to retrieve
        - index (int): index of the position in the argument list (starts from 0)
        - tab (str): string to add at the beginning of each line.
        - suffix: suffix to add after the variable
        """
        if suffix is None:
            suffix = self.default_suffix
        before = self.before_cstr(argname, tab, suffix)

        form = (
            '{tab}MTensor mtensor_{argname}{suffix} = MArgument_getMTensor(Args{suffix}[{index}]);\n'
            '{tab}{self.basetype.c_math_name} * data_{argname}{suffix} = libData{suffix}->MTensor_get{self.basetype.math_name}Data(mtensor_{argname}{suffix});\n')

        return form.format(argname=argname, self=self, tab=tab, index=index, suffix=suffix) + before

    def prototype_cstr(self, argname):
        """
        Returns a C string representing the declaration in a prototype argument.
        """
        return self.basetype.c_name + ' * ' + argname