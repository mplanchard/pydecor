"""
A module housing the decorators provided in the public API of PyDecor
"""

from __future__ import absolute_import, unicode_literals

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


def before(func, pass_params=True, pass_decorated=False,
           implicit_method_decoration=True, instance_methods_only=False,
           unpack_extras=True, extras_key='extras', **extras):
    """Specify a callable to be run before the decorated resource

    :param Callable func: a function to be called with the decorated
        function's args and kwargs, along with any keyword arguments
        passed to the decorator. This function should either return
        ``None``, or it should return a tuple of the form (args,
        kwargs), which will replace the args and kwargs with which the
        decorated function was called.
    :param bool pass_params: if True (the default), the arguments to the
        decorated function will be passed to the provided ``func``.
    :param bool pass_decorated: if True, a reference to the decorated
        function will be passed to the provided ``func``
    :param bool implicit_method_decoration:
    :param bool unpack_extras: if ``True`` (the default), any
        extra keyword arguments included in the decorator call will be
        passed as keyword arguments to ``func``. If ``False``, extra
        keyword arguments will be passed to func as a dict assigned to
        the keyword argument corresponding to ``key`` (default
        ``'passed_kwargs'``
    :param str extras_key: the key to which to assign extra decorator keyword
        arguments when ``unpack`` is ``False`` (default
        ``'passed_kwargs'``
    :param dict extras: any extra keyword arguments supplied
        to the decoration
    
    :return: the decorated function/method
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function that returns a replacement for the original"""

        def wrapper(*args, **kwargs):
            """The function that replaces the decorated one"""

            # import ipdb; ipdb.set_trace()

            fkwargs = extras if unpack_extras else {extras_key: extras}

            fn = func

            if pass_params:
                fn = partial(fn, args, kwargs)

            if pass_decorated:
                fn = partial(fn, decorated)

            fret = fn(**fkwargs)

            if fret is not None:
                args, kwargs = fret

            ret = decorated(*args, **kwargs)
            return ret

        if implicit_method_decoration and isclass(decorated):
            return ClassWrapper.wrap(
                decorated,
                decorator,
                instance_methods_only=instance_methods_only
            )

        # Equivalent to @wraps(decorated) on `wrapper`
        return wraps(decorated)(wrapper)

    return decorator


def after(func, pass_params=False, pass_result=True, pass_decorated=False,
          implicit_method_decoration=True, instance_methods_only=False,
          unpack_extras=True, extras_key='extras', **extras):
    """Specify a callable to be run after the decorated resource

    :param Callable func:
    :param bool pass_params:
    :param bool pass_result:
    :param bool pass_decorated:
    :param bool implicit_method_decoration:
    :param bool unpack_extras:
    :param str extras_key:
    :param dict extras:

    :return:
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function that returns a replacement for the original"""

        def wrapper(*args, **kwargs):
            """The function that replaces the decorated one"""

            ret = decorated(*args, **kwargs)

            fn = func

            if pass_result:
                fn = partial(fn, ret)

            if pass_params:
                fn = partial(fn, args, kwargs)

            if pass_decorated:
                fn = partial(fn, decorated)

            fkwargs = extras if unpack_extras else {extras_key: extras}

            fret = fn(**fkwargs)

            if fret is not None:
                return fret

            return ret

        if implicit_method_decoration and isclass(decorated):
            return ClassWrapper.wrap(
                decorated,
                decorator,
                instance_methods_only=instance_methods_only
            )

        # Equivalent to @wraps(decorated) on `wrapper`
        return wraps(decorated)(wrapper)

    return decorator


def instead(func, pass_params=True, pass_decorated=True,
            implicit_method_decoration=True, instance_methods_only=False,
            unpack_extras=True, extras_key='extras', **extras):
    """Specify a callable to be run in hte place of the decorated resource

    :param Callable func:
    :param bool pass_params:
    :param bool pass_decorated:
    :param bool implicit_method_decoration:
    :param bool unpack_extras:
    :param str extras_key:
    :param dict extras:
    """

    def decorator(decorated):
        """The function that returns a replacement for the original"""

        def wrapper(*args, **kwargs):
            """The function that replaces the decorated one"""

            fn = func

            if pass_params:
                fn = partial(fn, args, kwargs)

            if pass_decorated:
                fn = partial(fn, decorated)

            fkwargs = extras if unpack_extras else {extras_key: extras}

            return fn(**fkwargs)

        if implicit_method_decoration and isclass(decorated):
            return ClassWrapper.wrap(
                decorated,
                decorator,
                instance_methods_only=instance_methods_only
            )

        # Equivalent to @wraps(decorated) on `wrapper`
        return wraps(decorated)(wrapper)

    return decorator


def decorate(before=None, after=None, instead=None, before_opts=None,
             after_opts=None, instead_opts=None,
             implicit_method_decoration=True,
             instance_methods_only=False, unpack_extras=True,
             extras_key='extras', **extras):
    """

    :param Callable before:
    :param Callable after:
    :param Callable instead:
    :param dict before_opts:
    :param dict after_opts:
    :param dict instead_opts:
    :param implicit_method_decoration:
    :param unpack_extras:
    :param extras_key:
    :param extras:
    """

    if all(arg is None for arg in (before, after, instead)):
        raise ValueError(
            'At least one of "before," "after," or "instead" must be provided'
        )

    my_before = before
    my_after = after
    my_instead = instead

    before_opts = before_opts or {}
    after_opts = after_opts or {}
    instead_opts = instead_opts or {}

    for opts in (before_opts, after_opts, instead_opts):
        # Implicit method decoration cannot be mixed
        opts['implicit_method_decoration'] = implicit_method_decoration

    def decorator(decorated):

        wrapped = decorated

        if my_instead is not None:

            global instead
            dec_kwargs = _kwargs_from_opts(
                instead_opts, unpack_extras, extras_key, extras
            )
            wrapped = instead(my_instead, **dec_kwargs)(wrapped)

        if my_before is not None:

            global before
            dec_kwargs = _kwargs_from_opts(
                before_opts, unpack_extras, extras_key, extras
            )
            wrapped = before(my_before, **dec_kwargs)(wrapped)

        if my_after is not None:

            global after

            dec_kwargs = _kwargs_from_opts(
                after_opts, unpack_extras, extras_key, extras
            )
            wrapped = after(my_after, **dec_kwargs)(wrapped)

        def wrapper(*args, **kwargs):

            return wrapped(*args, **kwargs)

        if implicit_method_decoration and isclass(wrapped):
            return ClassWrapper.wrap(
                decorated,
                decorator,
                instance_methods_only=instance_methods_only
            )

        return wraps(decorated)(wrapper)

    return decorator


def _kwargs_from_opts(opts, unpack_extras, extras_key, extras):
    kwargs = opts
    if opts.get('unpack_extras', unpack_extras):
        kwargs.update(extras)
    else:
        key = opts.get('extras_key', extras_key)
        kwargs[key] = extras
    return kwargs
