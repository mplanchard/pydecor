# -*- coding: UTF-8 -*-
"""
Functions to use for decorator construction
"""

from __future__ import absolute_import, unicode_literals


__all__ = (
    'intercept',
    'log_call',
)


from inspect import getmodule
from logging import getLogger
from six import raise_from
from sys import version_info


from .constants import LOG_CALL_FMT_STR
from ._memoization import convert_to_hashable


PY2 = version_info < (3, 0)


def intercept(decorated, catch=Exception, reraise=None, handler=None,
              err_msg=None, include_context=False):
    """Intercept an error and either re-raise, handle, or both

    Designed to be called via the ``instead`` decorator.

    :param Decorated decorated: decorated function information
    :param Type[Exception] catch: an exception to intercept
    :param Union[bool, Type[Exception]] reraise: if provided, will re-raise
        the provided exception, after running any provided
        handler callable. If ``False`` or ``None``, no exception
        will be re-raised.
    :param Callable[[Type[Exception]],Any] handler: a function
        to call with the caught exception as its only argument.
        If not provided, nothing will be done with the caught
        exception.
    :param str err_msg: if included will be used to instantiate
        the exception. If not included, the caught exception will
        be cast to a string and used instead
    :param include_context: if True, the previous exception will
        be included in the exception context.
    """
    try:
        return decorated(*decorated.args, **decorated.kwargs)

    except catch as exc:
        if handler is not None:
            handler(exc)

        if isinstance(reraise, bool):
            if reraise:
                raise

        elif reraise is not None:

            if err_msg is not None:
                new_exc = reraise(err_msg)
            else:
                new_exc = reraise(str(exc))

            context = exc if include_context else None
            raise_from(new_exc, context)


def log_call(decorated, logger=None, level='info',
             format_str=LOG_CALL_FMT_STR):
    """Log the parameters & results of a function call

    Designed to be called via the ``after`` decorator with
    ``pass_params=True`` and ``pass_decorated=True``. Use
    :any:`decorators.log_call` for easiest invocation.

    :param Decorated decorated: decorated function information
    :param Optional[logging.Logger] logger: optional logger instance
    :param Optional[str] level: log level - must be an acceptable Python
        log level, case-insensitive
    :param format_str: the string to use when formatting the results
    """
    if logger is None:
        name = getmodule(decorated.wrapped).__name__
        logger = getLogger(name)
    log_fn = getattr(logger, level.lower())
    msg = format_str.format(
        name=decorated.wrapped.__name__,
        args=decorated.args,
        kwargs=decorated.kwargs,
        result=decorated.result
    )
    log_fn(msg)


def memoize(decorated, memo):
    """Return a memoized result if possible; store if not present

    :param Decorator decorated: decorated function information
    :param memo: the memoization cache. Must support standard
        __getitem__ and __setitem__ calls
    """
    key = convert_to_hashable(decorated.args, decorated.kwargs)
    if key in memo:
        return memo[key]
    res = decorated(*decorated.args, **decorated.kwargs)
    memo[key] = res
    return res
