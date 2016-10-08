#!/usr/bin/env python3

"""
Module with generic functions and methods.
"""

from path import Path


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


def iterate_folder(filename, pattern, excluding=None):
    """
    Iterates through files with names in the given pattern in the same
    folder as filename, excluding those that the basename matches one in excluding
    """
    path = Path(filename)
    if not path.isdir():
        path = filename.parent

    for f in Path(path).glob('*.py'):
        sentinel = False
        for exc in (excluding or []):
            if exc in f.basename():
                sentinel = True
                break
        if not sentinel:
            yield f
