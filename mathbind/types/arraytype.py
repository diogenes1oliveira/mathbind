#!/usr/bin/env python3

from mathbind.types import BasicType, BasicValueType


class ArrayType(BasicType):
    """
    Represents an array type.
    Attributes:
    - basetype (BasicValueType): base type of the pointer.
    - policy (str): size policy of the array. Can be 'fixed', 'infinite', 'variable' (tied to another variable).
    - size (str or int):
    - const (bool): can the parameter be changed?
    """

    templates = {
        'before_cstr': (
            '{tab}{basetype_c_name} * {argname} = ({basetype_c_name} *) data_{argname}{suffix};\n'
            '{tab}if(sizeof({basetype_c_math_name}) != sizeof({basetype_c_name})) {{\n'
            '{tab}{tab}{argname} = malloc(sizeof({basetype_c_name}) * {size});\n'
            '{tab}{tab}for(int i{suffix} = 0; i{suffix} < {size}; ++i{suffix})\n'
            '{tab}{tab}{tab}{argname}[i{suffix}] = data_{argname}Gen[i{suffix}];\n'
            '{tab}}}\n'
        ),
        'before_mathstr' : (
            '{tab}{argname}{suffix} = Developer`ToPackedArray[Map[{convert_f}, {argname}{suffix}]];\n'
        ),
        'after_cstr': (
            '{tab}if(sizeof({basetype_c_math_name}) != sizeof({basetype_c_name})) {{\n'
            '{tab}{tab}for(int i{suffix} = 0; i{suffix} < {size}; ++i{suffix})\n'
            '{tab}{tab}{tab}data_{argname}Gen[i{suffix}] = {argname}[i{suffix}];\n'
            '{tab}{tab}free({argname});\n'
            '{tab}}}\n'
            '{tab}libData{suffix}->MTensor_disownAll(mtensor_{argname}{suffix});\n'
        ),
        'retrieve_cstr':(
            '{tab}MTensor mtensor_{argname}{suffix} = MArgument_getMTensor(Args{suffix}[{index}]);\n'
            '{tab}{basetype_c_math_name} * data_{argname}{suffix} = '
            'libData{suffix}->MTensor_get{basetype_math_name}Data(mtensor_{argname}{suffix});\n'
        )
    }

    def __init__(self, basetype, policy, size=None, const=False):
        self.basetype = basetype
        self.typename = basetype.typename + ' [{}]'.format('' if size is None else size)
        self.policy = policy
        self.size = size
        self.const = const

    @property
    def should_return(self):
        return not self.const

    @property
    def math_name(self):
        return '{{{self.basetype.math_name}, 1, "Shared"}}'.format(self=self)

    @classmethod
    def from_str(cls, s):
        """
        Tries to build a new ArrayType from the string specification, failing if
        the type is value or pointer-like.
        """
        bracket1 = s.index('[')
        bracket2 = s.index(']')
        if bracket1 > bracket2 or s.count('[') != 1 or s.count(']') != 1:
            raise ValueError('Misplaced brackets')

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

        const = False
        if 'const' in type_spec.split():
            type_spec = ' '.join(type_spec.split()[1:])
            const = True

        return ArrayType(BasicValueType.from_str(type_spec), policy, size, const)

    @classmethod
    def from_prototype_cstr(cls, s):
        """
        Tries to extract (type, argname) from the string.
        """
        try:
            bra1, bra2 = s.index('['), s.index(']')
        except (IndexError, ValueError):
            raise ValueError('No brackets found')

        if bra1 > bra2:
            raise ValueError('Misplaced brackets')

        *words, argname = s[: bra1].split()
        return ArrayType.from_str(' '.join(words) + '[' + s[bra1 + 1:bra2] + ']'), argname

    def __eq__(self, other):
        return (self.basetype == other.basetype and self.policy == other.policy
                and self.size == other.size and self.const == other.const)

    def __repr__(self):
        return ('ArrayType(basetype=%r, policy=%r, size=%r, const=%r)'
                % (self.basetype, self.policy, self.size, self.const))

    def before_cstr(self, argname, tab='', suffix=None):
        """
        Returns a C string with the instructions to convert the argname from the
        Mathematica required format.
        """
        if suffix is None:
            suffix = self.default_suffix
        basetype_c_name = self.basetype.c_name
        basetype_c_math_name = self.basetype.c_math_name
        size = self.size
        return ArrayType.templates['before_cstr'].format(**locals())

    def before_mathstr(self, argname, tab='', suffix=None):
        if suffix is None:
            suffix = self.default_suffix

        convert_f = self.basetype.math_convert_f
        size = self.size
        form = ArrayType.templates['before_mathstr']

        return form.format(**locals())

    def after_cstr(self, argname, tab='', suffix=None):
        """
        Returns a C string with the instructions to convert the argname back to the
        Mathematica required format.
        """
        if suffix is None:
            suffix = self.default_suffix
        basetype_c_name = self.basetype.c_name
        basetype_c_math_name = self.basetype.c_math_name
        size = self.size
        return ArrayType.templates['after_cstr'].format(**locals())

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
        basetype_math_name = self.basetype.math_name
        basetype_c_math_name = self.basetype.c_math_name

        return ArrayType.templates['retrieve_cstr'].format(**locals()) + before

    def prototype_cstr(self, argname):
        """
        Returns a C string representing the declaration in a prototype argument.
        """
        return self.basetype.c_name + ' * ' + argname