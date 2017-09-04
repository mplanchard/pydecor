# -*- coding: UTF-8 -*-
"""
Tests for memoization functions
"""

import pytest

from pydecor._memoization import hashable


@pytest.mark.parametrize('item', [
    'foo',
    12,
    12.5,
    7e7,
    {'foo': 'bar'},
    object(),
    type('a', (object, ), {}),
    type('a', (object, ), {})(),
    lambda x: 'foo',
    {'a', 'b', 'c'},
    ('a', 'b', 'c'),
    ['a', 'b', 'c'],
    ('a', {'b': 'c'}, ['d']),
    ['a', ('b', 'c'), {'d': 'e'}],
])
def test_hashable(item):
    """Test getting a hashable verison of an item

    Asserts that the hash method does not error, which it does
    if the returned item is unhashable
    """
    hash(hashable(item))
