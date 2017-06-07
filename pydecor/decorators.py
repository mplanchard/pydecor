"""
A module housing the decorators provided in the public API of PyDecor
"""

from inspect import isclass
from logging import getLogger
from functools import partial, wraps
from types import FunctionType, MethodType
from typing import Union

from ._util import ClassWrapper


__all__ = (
    'after',
    'before',
    'DecoratorType',
)


log = getLogger(__name__)


DecoratorType = Union[FunctionType, MethodType, type]


def before(func, with_params=True, unpack_passed=True,
           passed_key='passed', **passed):
    """Specify a callable to be run before the decorated resource

    :param Callable func: a function to be called with the decorated
        function's args and kwargs, along with any keyword arguments
        passed to the decorator. This function should either return
        ``None``, or it should return a tuple of the form (args,
        kwargs), which will replace the args and kwargs with which the
        decorated function was called.
    :param bool with_params: if True (the default), the arguments to the
        decorated function will be passed to the provided ``func``.
    :param bool unpack_passed: if ``True`` (the default), any
        extra keyword arguments included in the decorator call will be
        passed as keyword arguments to ``func``. If ``False``, extra
        keyword arguments will be passed to func as a dict assigned to
        the keyword argument corresponding to ``key`` (default
        ``'passed_kwargs'``
    :param str passed_key: the key to which to assign extra decorator keyword
        arguments when ``unpack`` is ``False`` (default
        ``'passed_kwargs'``
    :param dict passed: any extra keyword arguments supplied
        to the decoration
    
    :return: the decorated function/method
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function returned in place of the decorated function"""

        def wrapper(*args, **kwargs):
            """The function called in place of the wrapped function"""
            fargs = (args, kwargs) if with_params else ()
            fkwargs = passed if unpack_passed else {passed_key: passed}

            fret = func(*fargs, **fkwargs)

            if fret is not None:
                args, kwargs = fret

            ret = decorated(*args, **kwargs)
            return ret

        if isclass(decorated):
            return ClassWrapper.wrap(decorated, decorator)

        # Equivalent to @wraps(decorated) on `wrapper`
        return wraps(decorated)(wrapper)

    return decorator


def after(func, with_params=False, with_result=True, unpack_passed=True,
          passed_key='passed', **passed):
    """Specify a callable to be run after the decorated resource

    :param Callable func:
    :param bool with_params:
    :param bool with_result:
    :param bool unpack_passed:
    :param str passed_key:
    :param dict passed:

    :return:
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function returned in place of the original function"""

        @wraps(decorated)
        def wrapper(*args, **kwargs):
            """The function called in place of the wrapped function"""

            ret = decorated(*args, **kwargs)

            fn = func

            if with_result:
                fn = partial(fn, ret)

            if with_params:
                fn = partial(fn, args, kwargs)

            fkwargs = passed if unpack_passed else {passed_key: passed}

            fret = fn(**fkwargs)

            if fret is not None:
                return fret

            return ret

        if isclass(decorated):
            return ClassWrapper.wrap(decorated, decorator)

        # Equivalent to @wraps(decorated) on `wrapper`
        return wraps(decorated)(wrapper)

    return decorator
