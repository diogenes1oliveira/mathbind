#!/usr/bin/env python3

from mathbind.generic import iterate_subtypes


class BasicType:
    """
    Represents the interface to a basic generic type.

    Class properties:
    - default_suffix (str): string to add to each generated identifier, used
    to avoid clashes.
    - default_value  (str): default value of the type, defaults to '0'

    Instance properties
    - typename (str): real typename, as declared
    """
    default_suffix = 'Gen'
    default_value = '0'

    @classmethod
    def from_str(cls, s):
        """
        Builds a type from a string with the type specification.
        """
        for sub in iterate_subtypes(cls):
            try:
                return sub.from_str(s)
            except ValueError:
                continue
        else:
            raise ValueError('No adequate type was found')

    @classmethod
    def from_prototype_cstr(cls, s):
        """
        Tries to extract (type, argname) from the string containing a variable
        declaration of the specified argument.

        Example: from_prototype_cstr('int arg1')
        """
        for sub in iterate_subtypes(cls):
            try:
                return sub.from_prototype_cstr(s)
            except ValueError:
                continue
        else:
            raise ValueError('No adequate type was found')

    def pass_cstr(self, argname):
        """
        Returns a C string that represents how to pass the variable in a
        function call, defaults to the own argname (pass by value).
        """
        return argname

    def before_cstr(self, argname, tab='', suffix=None):
        """
        Returns a C string with the instructions to convert the argname from the
        Mathematica required format, defaults to ""
        Args:
        - argname (str): name of the argument to retrieve
        - tab (str): string to add at the beginning of each line.
        - suffix (str): suffix to add after the variable, defaults to None
        """
        return ''

    def before_mathstr(self, argname, tab='', suffix=None):
        '''
        Returns a Mathematica string with the instructions to convert the
        Mathematica object before passing it to the C generated function, defaults
        to "".
        Args:
        - argname (str): name of the argument to retrieve
        - tab (str): string to add at the beginning of each line.
        - suffix (str): suffix to add after the variable, defaults to None
        '''
        return ''
    
    def after_cstr(self, argname, tab='', suffix=None):
        """
        Code to add after calling the function, defaults to an empty string.
        Args:
        - argname (str): name of the argument to retrieve
        - tab (str): string to add at the beginning of each line.
        - suffix (str): suffix to add after the variable, defaults to None
        """
        return ""

    def retrieve_cstr(self, argname, index, tab='', suffix=None):
        """
        Returns a C string to retrieve the argument from the Mathematica call
        scheme.

        Args:
        - argname (str): name of the argument to retrieve
        - index (int): index of the position in the argument list (starts from 0) 
        - tab (str): string to add at the beginning of each line.
        - suffix: suffix to add after the variable
        """
        raise NotImplemented

    def return_cstr(self, func_call, tab='', suffix=None):
        """
        Returns a C string with the code to call the function, retrieve the
        return value and send it to Mathematica.

        Args:
        - func_call (str): string to effectively call the function.
        - tab (str): string to add at the beginning of each line.
        - suffix: suffix to add after the variable
        """
        raise NotImplemented

    def prototype_cstr(self, argname):
        """
        Returns a C string representing the declaration in a prototype argument.
        """
        raise NotImplemented

    def prototype_return_cstr(self):
        """
        Returns a C string representing the declaration in a prototype return.
        """
        raise NotImplemented