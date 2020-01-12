# EMACS settings: -*- coding: utf-8 -*-
"""
Decorators controlling visibility of entities in a Python module.
"""

__all__ = [
    'export',
]
__api__ = __all__

import sys


def export(entity):
    """
    Register the given entity as public accessible in a module.
    """

    # * Based on an idea by Duncan Booth:
    #   http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
    # * Improved via a suggestion by Dave Angel:
    #   http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1

    module = sys.modules[entity.__module__]
    if hasattr(module, '__all__'):
        if entity.__name__ not in module.__all__:
            module.__all__.append(entity.__name__)
    else:
        module.__all__ = [ entity.__name__ ]

    return entity
