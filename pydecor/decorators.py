"""
A module housing the decorators provided in the public API of PyDecor
"""

from logging import getLogger
from functools import partial, wraps
from types import FunctionType, MethodType
from typing import Callable, Union


__all__ = (
    'after',
    'before',
    'DecoratorType',
)


log = getLogger(__name__)


DecoratorType = Union[FunctionType, MethodType, type]


def before(func, unpack=True, key='decorator_kwargs',
           **decorator_kwargs):
    """Specify a callable to be run before the decorated resource

    :param func: a function to be called with the decorated function's
        args and kwargs, along with any keyword arguments passed to
        the decorator. This function should either return ``None``,
        or it should return a tuple of the form (args, kwargs),
        which will replace the args and kwargs with which the
        decorated function was called.
    :param unpack: if ``True`` (the default), any extra keyword
        arguments included in the decorator call will be passed as
        keyword arguments to ``func``. If ``False``, extra keyword
        arguments will be passed to func as a dict assigned to the
        keyword argument corresponding to ``key`` (default
        ``'decorator_kwargs'``
    :param key: the key to which to assign extra decorator keyword
        arguments when ``unpack`` is ``False`` (default
        ``'decorator_kwargs'``
    :param decorator_kwargs: any extra keyword arguments supplied
        to the decoration
    
    :return: the decorated function/method
    """

    def decorator(decorated):
        """The function returned in place of the decorated function"""

        @wraps(decorated)
        def wrapper(*args, **kwargs):
            """The function called in place of the wrapped function"""
            if unpack:
                func_kwargs = decorator_kwargs
            else:
                func_kwargs = {key: decorator_kwargs}

            fret = func(args, kwargs, **func_kwargs)

            if fret is not None:
                args, kwargs = fret

            ret = decorated(*args, **kwargs)
            return ret

        return wrapper

    return decorator


def after(func, with_result=True, unpack=True, key='decorator_kwargs',
          **decorator_kwargs):
    """Specify a callable to be run after the decorated resource

    :param func:
    :param with_result:
    :param unpack:
    :param key:
    :param decorator_kwargs:
    :return:
    """

    def decorator(decorated):
        """The function returned in place of the original function"""

        @wraps(decorated)
        def wrapper(*args, **kwargs):
            """The function called in place of the wrapped function"""

            ret = decorated(*args, **kwargs)

            if unpack:
                func_kwargs = decorator_kwargs
            else:
                func_kwargs = {key: decorator_kwargs}

            if with_result:
                fret = func(args, kwargs, ret, **func_kwargs)
            else:
                fret = func(args, kwargs, **func_kwargs)

            if fret is not None:
                return fret

            return ret

        return wrapper

    return decorator
