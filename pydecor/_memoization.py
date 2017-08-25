"""
Required functionality for the memoization function
"""

try:
    import cPickle as pickle  # Python 2.7
except ImportError:
    import pickle  # Python 3 automatically uses cpickle if available


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
