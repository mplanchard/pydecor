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


PY2 = version_info < (3, 0)


def intercept(decorated_args, decorated_kwargs, decorated, catch=Exception,
              reraise=None, handler=None, err_msg=None, include_context=False):
    """Intercept an error and either re-raise, handle, or both

    Designed to be called via the ``instead`` decorator.

    :param Callable decorated: the decorated function
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
        return decorated(*decorated_args, **decorated_kwargs)

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


def log_call(result, args, kwargs, func, logger=None, level='info',
             format_str=LOG_CALL_FMT_STR):
    """Log the parameters & results of a function call

    Designed to be called via the ``after`` decorator with
    ``pass_params=True`` and ``pass_decorated=True``. Use
    :any:`decorators.log_call` for easiest invocation.

    :param Any result: the result of the function
    :param tuple args: the function's call args
    :param dict kwargs: the function's call kwargs
    :param Callable func: the function itself
    :param Optional[logging.Logger] logger: optional logger instance
    :param Optional[str] level: log level - must be an acceptable Python
        log level, case-insensitive
    :param format_str: the string to use when formatting the results
    """
    if logger is None:
        name = getmodule(func).__name__
        logger = getLogger(name)
    log_fn = getattr(logger, level.lower())
    msg = format_str.format(
        name=func.__name__,
        args=args,
        kwargs=kwargs,
        result=result
    )
    log_fn(msg)
