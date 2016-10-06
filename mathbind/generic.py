#!/usr/bin/env python3

"""
Module with generic functions and methods.
"""


def iterate_subtypes(cls, visited=None):
    """
    Iterates through all the derived subtypes.
    """
    subs = cls.__subclasses__()
    if visited is None:
        visited = set()

    for sub in subs:
        if sub not in visited:
            visited.add(sub)
        yield sub

        for subsub in iterate_subtypes(sub, visited):
            yield subsub