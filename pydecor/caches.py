"""
Caches for memoization
"""


from collections import OrderedDict
from datetime import datetime


class LRUCache(OrderedDict):
    """Remove least-recently used items

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
    """Removes the first input item when full

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
    """Remove items older than the specified time

    When trying to access an entry, either via ``in`` or
    ``__getitem__``, if it is older than the specified
    ``max_age``, in seconds, it will be deleted, and the
    data structure will act as though it does not exist.

    :param int max_age: age in seconds beyond which entries
        should be considered invalid. The default is 0, which
        means that entries should be stored forever.
    """

    def __init__(self, max_age=0, *args, **kwargs):
        super(TimedCache, self).__init__(*args, **kwargs)
        self._max_age = max_age

    def __getitem__(self, key):
        value, last_time = dict.__getitem__(self, key)
        now = datetime.utcnow().timestamp()
        if self._max_age and now - last_time > self._max_age:
            del self[key]
            raise KeyError(key)
        else:
            return value

    def __setitem__(self, key, value):
        now = datetime.utcnow().timestamp()
        dict.__setitem__(self, key, (value, now))

    def __contains__(self, key):
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True
