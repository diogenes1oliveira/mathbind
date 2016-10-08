#!/usr/bin/env python3

from mathbind.generic import iterate_subtypes


class Compiler:
    """
    A base class for all compilers.
    """
    @classmethod
    def by_name(cls, name):
        """
        Finds the compiler class by name.
        """
        for t in iterate_subtypes(cls):
            if t.name == 'name':
                return t
        else:
            raise ValueError("Compiler %r not found" % name)