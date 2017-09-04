# -*- coding: UTF-8 -*-
"""
Prête-à-porte (ready-to-wear) decorators are ready to be used immediately
in your codebase, minimal thinking required.
"""

from __future__ import absolute_import, unicode_literals


__all__ = (
    'intercept',
    'log_call',
    'memoize',
)


from logging import getLogger

from pydecor import functions
from pydecor.constants import LOG_CALL_FMT_STR
from pydecor.caches import LRUCache

from .generic import instead, after


log = getLogger(__name__)


def intercept(catch=Exception, reraise=None, handler=None, err_msg=None,
              include_context=False):
    """Intercept an exception and either re-raise, handle, or both

    Example:

    .. code:: python

        from logging import getLogger
        from pydecor import intercept

        log = getLogger(__name__)

        class MyLibraryError(Exception):
            pass

        def error_handler(exception):
            log.exception(exception)

        # Re-raise and handle
        @intercept(catch=ValueError, reraise=MyLibraryError,
                   handler=error_handler):
        def some_error_prone_function():
            return int('foo')

        # Re-raise only
        @intercept(catch=TypeError, reraise=MyLibraryError)
        def another_error_prone_function(splittable_string):
            return splittable_string.split('/', '.')

        # Handle only
        @intercept(catch=ValueError, handle=error_handler)
        def ignorable_error(some_string):
            # Just run the handler on error, rather than re-raising
            log.info('This string is {}'.format(int(string)))


    :param Type[Exception] catch: the exception to catch
    :param Union[bool, Type[Exception]] reraise: the exception to
        re-raise or ``True``. If an exception is provided, that
        exception will be raised. If ``True``, the original
        exception will be re-raised. If ``False`` or ``None``,
        no exception will be raised. Note that if a ``handler``
        is provided, it will always be called prior to re-raising.
    :param Callable[[Type[Exception]],Any] handler: a function to call
        with the caught exception as its only argument. If not provided,
        nothing will be done with the caught exception
    :param str err_msg: An optional string with which to call the
        re-raised exception. If not provided, the caught exception
        will be cast to a string and used instead.
    :param include_context: if True, the previous exception will be
        included in the context of the re-raised exception, which
        means the traceback will show both exceptions, noting that
        the first exception "was the direct cause of the following
        exception"
    """
    return instead(
        functions.intercept,
        _use_future_syntax=True,
        catch=catch,
        reraise=reraise,
        handler=handler,
        err_msg=err_msg,
        include_context=include_context,
    )


def log_call(logger=None, level='info', format_str=LOG_CALL_FMT_STR):
    """Log the name, parameters, & result of a function call

    If not provided, a logger instance will be retrieved corresponding
    to the module name of the decorated function, so if you decorate
    the function ``do_magic()`` in the module ``magic.py``, the
    retrieved logger will be the same as one retrieved in ``magic.py``
    with ``logging.getLogger(__name__)``

    The ``level`` provided here **does not** set the log level of the
    passed or retrieved logger. It just determines what level the
    generated message should be logged with.

    Example:

    * Assume the following is found in ``log_example.py``

    .. code:: python

        from pydecor import log_call

        @log_call
        def return_none(*args, **kwargs):
            return None

        return_none('alright', my='man')

        # Will retrieve the ``log_example`` logger
        # and log the message:
        # "return_none(*('alright', ), **{'my': 'man'}) -> None"

    :param Optional[logging.Logger] logger: an optional Logger
        instance. If not provided, the logger corresponding to the
        decorated function's module name will be retrieved
    :param str level: the level with which to log the message. Must
        be an acceptable Python log level
    :param str format_str: the format string to use when interpolating
        the message. This defaults to
        ``'{name}(*{args}, **{kwargs}) -> {result}'``. Any provided
        format string should contain the same keys, which will be
        interpolated appropriately.

    :rtype: DecoratorType
    """
    return after(
        functions.log_call,
        _use_future_syntax=True,
        logger=logger,
        level=level,
        format_str=format_str,
    )


def memoize(keep=0, cache_class=LRUCache):
    """Memoize the decorated function

    The default cache is an infinitely growing LRU Cache. To specify
    a maximum number of key/value pairs to keep, specify ``keep``.
    To specify a different cache, pass it to ``cache_class``. Any
    class that implements ``__contains__``, ``__getitem__``, and
    ``__setitem__`` may be used. as the cache. There are several
    cache types provided in `pydecor.caches`_.

    :param int keep: the maximum size of the cache (or max age of the
        cache entries in seconds when using TimedCache). By default
        this is 0, which means the cache can grow indefinitely.
    :param cache_class: the cache to store function results.
        Any class that supports __getitem__, __setitem__,
        and __contains__ should work just fine here. The
        max_size is passed in as an instantiation parameter,
        so that should also be supported. In addition to
        the default LRUCache, a LIFOCache and a TimedCache
        are provided in ``pydecor.caches``.

    :rtype: DecoratorType
    """
    return instead(
        functions.memoize,
        _use_future_syntax=True,
        memo=cache_class(keep),
    )
