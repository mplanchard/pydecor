"""
Functions to use for decorator construction
"""

from __future__ import absolute_import, unicode_literals


__all__ = (
    'interceptor',
)


def interceptor(decorated_args, decorated_kwargs, decorated, catch=Exception,
                reraise=None, handler=None):
    """Intercept an error and either re-raise, handle, or both

    Designed to be called via the ``instead`` decorator.

    :param Callable decorated: the decorated function
    :param Type[Exception] catch: an exception to intercept
    :param Type[Exception] reraise: if provided, will re-raise
        the provided exception, after running any provided
        handler callable
    :param Callable[[Type[Exception]],Any] handler: a function
        to call with the caught exception as its only argument.
        If not provided, nothing will be done with the caught
        exception.
    """
    try:
        return decorated(*decorated_args, **decorated_kwargs)
    except catch as exc:
        if handler is not None:
            handler(exc)
        if reraise is not None:
            raise reraise from None
