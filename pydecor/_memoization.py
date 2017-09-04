# -*- coding: UTF-8 -*-
"""
Required functionality for the memoization function
"""

__all__ = (
    'convert_to_hashable',
    'hashable',
)

import dill as pickle


def convert_to_hashable(args, kwargs):
    """Return args and kwargs as a hashable tuple"""
    return hashable(args), hashable(kwargs)


def hashable(item):
    """Get return a hashable version of an item

    If the item is natively hashable, return the item itself. If
    it is not, return it dumped to a pickle string.
    """
    try:
        hash(item)
    except TypeError:
        item = pickle.dumps(item)
    return item
