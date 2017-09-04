# -*- coding: UTF-8 -*-
"""
Caches for memoization
"""

from __future__ import absolute_import, unicode_literals


__all__ = (
    'LRUCache',
    'FIFOCache',
    'TimedCache',
)


from collections import OrderedDict
from time import time


class LRUCache(OrderedDict):
    """Self-pruning cache using an LRU strategy

    If instantiated with a ``max_size`` other than ``0``, will
    automatically prune the least-recently-used (LRU) key/value
    pair when inserting an item after reaching the specified size.

    An item is considered to be "used" when it is inserted or
    accessed, at which point its position in recently used
    queue is updated to the most recent.

    Supports all standard dictionary methods.

    :param int max_size: maximum number of entries to save
        before pruning
    """

    def __init__(self, max_size=0, *args, **kwargs):
        super(LRUCache, self).__init__(*args, **kwargs)
        self._max_size = max_size

    def __getitem__(self, key, **kwargs):
        value = OrderedDict.__getitem__(self, key)
        del self[key]
        OrderedDict.__setitem__(self, key, value, **kwargs)
        return value

    def __setitem__(self, key, value, **kwargs):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value, **kwargs)
        if self._max_size and len(self) > self._max_size:
            self.popitem(last=False)


class FIFOCache(OrderedDict):
    """Self-pruning cache using a FIFO strategy

    If instantiated with a ``max_size`` other than ``0``, will
    automatically prune the least-recently-inserted key/value
    pair when inserting an item after reaching the specified
    size.

    Supports all standard dictionary methods.

    :param int max_size: maximum number of entries to save
        before pruning
    """

    def __init__(self, max_size=0, *args, **kwargs):
        super(FIFOCache, self).__init__(*args, **kwargs)
        self._max_size = max_size

    def __setitem__(self, key, value, **kwargs):
        OrderedDict.__setitem__(self, key, value)
        if self._max_size and len(self) > self._max_size:
            self.popitem(last=False)


class TimedCache(dict):
    """Self-pruning cache whose entries can be set to expire

    If instantiated with a ``max_age`` other than ``0``, will
    consider entries older than the specified age to be invalid,
    removing them from the cache upon an attempt to access them
    and returning as though they do not exist.

    Supports all standard dictionary methods.

    :param int max_age: age in seconds beyond which entries
        should be considered invalid. The default is 0, which
        means that entries should be stored forever.
    """

    def __init__(self, max_age=0, *args, **kwargs):
        super(TimedCache, self).__init__(*args, **kwargs)
        self._max_age = max_age

    def __getitem__(self, key):
        value, last_time = dict.__getitem__(self, key)
        now = time()
        if self._max_age and now - last_time > self._max_age:
            del self[key]
            raise KeyError(key)
        else:
            return value

    def __setitem__(self, key, value):
        now = time()
        dict.__setitem__(self, key, (value, now))

    def __contains__(self, key):
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True
