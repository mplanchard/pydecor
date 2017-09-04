# -*- coding: UTF-8 -*-
"""
Generic decorators help you to easily create your own decorators with simple
``@before``, ``@after``, and ``@instead`` decorators that call a function
as specified in the execution order of the decorated callable.

Additionally the ``@decorate`` decorator allows you to combine the above three
generics in one call, and the ``construct_decorator`` function returns a
ready-to-use decorator implementing any or all of the above three generics,
which you can then assign to a variable name and use as desired.
"""

from __future__ import absolute_import, unicode_literals


__all__ = (
    'after',
    'before',
    'construct_decorator',
    'decorate',
    'instead',
    'Decorated',
    'DecoratorType',
)


from inspect import isclass
from logging import getLogger
from functools import partial, wraps
from types import FunctionType, MethodType
from typing import Union

from ._utility import ClassWrapper, get_fn_args


log = getLogger(__name__)


DecoratorType = Union[FunctionType, MethodType, type]


class Decorated(object):
    """A representation of a decorated class

    This user-immutable object provides information about the decorated
    class, method, or function. The decorated callable can be called
    by directly calling the ``Decorated`` instance, or via the
    ``wrapped`` instance attribute.

    The example below illustrates direct instantiation of the
    ``Decorated`` class, but generally you will only deal with
    instances of this class when they are passed to the functions
    specified on generic decorators.

    .. code:: python

        from pydecor import Decorated

        def some_function(*args, **kwargs):
            return 'foo'

        decorated = Decorated(some_function, ('a', 'b'), {'c': 'c'})

        assert decorated.wrapped.__name__ == some_function.__name__
        assert decorated.args == ('a', 'b')
        assert decorated.kwargs == {'c': 'c'}
        assert decorated.result is None  # has not yet been called

        res = decorated(decorated.args, decorated.kwargs)

        assert 'foo' == res == decorated.result

    .. note::

        identity tests ``decorated.wrapped is some_decorated_function``
        will not work on the ``wrapped`` attribute of a ``Decorated``
        instance, because internally the wrapped callable is wrapped
        in a method that ensures that ``Decorated.result`` is set
        whenever the callable is called. It is wrapped using
        ``functools.wraps``, so attributes like ``__name__``,
        ``__doc__``, ``__module__``, etc. should still be the
        same as on an actual reference.

        If you need to access a real reference to the wrapped
        function for any reason, you can do so by accessing
        the ``__wrapped__`` property, on ``wrapped``, which is
        set by ``functools.wraps``, e.g.
        ``decorated.wrapped.__wrapped__``.

    :param wrapped: a reference to the wrapped callable. Calling the
        wrapped callable via this reference will set the ``result``
        attribute.
    :param args: a tuple of arguments with which the decorated function
        was called
    :param kwargs: a dict of arguments with which the decorated function
        was called
    :param result: either ``None`` if the wrapped callable has not yet
        been called or the result of that call
    """

    __slots__ = ('args', 'kwargs', 'wrapped', 'result')

    def __init__(self, wrapped, args, kwargs, result=None):
        """Instantiate a Decorated object

        :param callable wrapped: the callable object being wrapped
        :param tuple args: args with which the callable was called
        :param dict kwargs: keyword arguments with which the callable
            was called
        :param
        """
        sup = super(Decorated, self)
        sup.__setattr__('args', get_fn_args(wrapped, args))
        sup.__setattr__('kwargs', kwargs)
        sup.__setattr__('wrapped', self._sets_results(wrapped))
        sup.__setattr__('result', result)

    def __str__(self):
        """Return a nice string of self"""
        if hasattr(self.wrapped, '__name__'):
            name = self.wrapped.__name__
        else:
            name = str(self.wrapped)
        return '<Decorated {}({}, {})>'.format(name, self.args, self.kwargs)

    def __call__(self, *args, **kwargs):
        """Call the function the specified arguments.

        Also set ``self.result``
        """
        return self.wrapped(*args, **kwargs)

    def __setattr__(self, key, value):
        """Disallow attribute setting"""
        raise AttributeError(
            'Cannot set "{}" because {} is immutable'.format(key, self)
        )

    def _sets_results(self, wrapped):
        """Ensure that calling ``wrapped()`` sets the result attr

        :param callable wrapped: the wrapped function, class, or method
        """
        @wraps(wrapped)
        def wrapped_wrapped(*args, **kwargs):
            """Set self.result after calling wrapped"""
            res = wrapped(*args, **kwargs)
            super(Decorated, self).__setattr__('result', res)
            return res

        return wrapped_wrapped


def before(func, pass_params=False, pass_decorated=False,
           implicit_method_decoration=True, instance_methods_only=False,
           unpack_extras=True, extras_key='extras',
           _use_future_syntax=False, **extras):
    """Specify a callable to be run before the decorated resource

    A callable provided to this decorator will be called
    any time the decorated function is executed, immediately before
    its execution.

    The callable is expected to either return ``None`` or to return
    a tuple and dict with which to replace the arguments to the
    decorated function.

    By default, the provided callable is called with no arguments
    and only any keyword arguments provided as extras to the
    decoration call::

        (**extras)

    However, this is configurable. If all possible ``pass``
    parameters are True, the call signature would look like this::

        (decorated_args, decorated_kwargs, decorated, **extras)

    Items that are omitted will be removed from the call signature.
    For example, specifying ``pass_params=False`` and
    ``pass_decorated=True`` would adjust the call signature to
    look like::

        (decorated, **extras)

    Specifying ``pass_params=True`` will pass the arguments and
    keyword arguments of the decorated function (as a tuple and
    a dict, respectively) to the provided callable.

    Specifying ``pass_decorated=True`` will pass a reference
    to the decorated function to the provided callable.

    Any extra keyword arguments passed to the decoration call
    will by default be passed directly as keyword arguments
    to ``func``. If keyword names conflict with the passed
    function, ``unpack_extras=False`` will cause extra keyword
    arguments to be passed as a dictionary using the value
    of ``extras_key``, which defaults to ``"extras"``.

    :param Callable func:
        a callable to run before the decorated function. By default,
        it is called with no arguments, but the call signature may
        be changed depending on the value of ``pass_params`` and
        ``pass_decorated``

    :param bool pass_params:
        (default False) if True, the arguments and keyword arguments to
        the decorated function will be passed to ``func`` as a tuple
        and a dict, respectively

    :param bool pass_decorated:
        (default False) if True, a reference to the decorated function
        will be passed to the provided ``func``

    :param bool implicit_method_decoration:
        (default True) if True, decorating a class implies decorating
        all of its methods

    :param bool instance_methods_only:
        (default False) if True, decorating a class implies decorating
        only its instance methods (not ``classmethod``- or
        ``staticmethod``- decorated methods)

    :param bool unpack_extras:
        (default True) if True, any extra keyword arguments included
        in the decorator call will be passed as keyword arguments
        to ``func``. If ``False``, extra keyword arguments will be
        passed to func as a dict assigned to the keyword argument
        corresponding to ``key``

    :param str extras_key:
        (default ``"extras"``) the key to which to assign extra
        decorator keyword arguments when ``unpack_extras`` is ``False``

    :param bool _use_future_syntax:
        (default False) if True, use the new ``Decorated`` object,
        which will become the default in version 2.0.0. If this
        parameter is True, all other parameters will be ignored
        expect for ``instance_methods_only`` and
        ``implicit_method_decoration``, a ``Decorated`` object
        will be passed to the function as its first argument,
        and any provided keyword arguments will be unpacked.

    :param **dict extras:
        any extra keyword arguments supplied to the decoration call

    :return: the decorated function/method/class
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function that returns a replacement for the original"""

        def wrapper(*args, **kwargs):
            """The function that replaces the decorated one"""

            if unpack_extras or _use_future_syntax:
                fkwargs = extras
            else:
                fkwargs = {extras_key: extras}

            fn = func
            decor = decorated

            if _use_future_syntax:
                decor = Decorated(decorated, args, kwargs)
                fn = partial(fn, decor)
            else:
                if pass_params:
                    fn_args = get_fn_args(decorated, args)
                    fn = partial(fn, fn_args, kwargs)

                if pass_decorated:
                    fn = partial(fn, decorated)

            fret = fn(**fkwargs)

            if fret is not None:
                args, kwargs = fret

            ret = decor(*args, **kwargs)
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
          unpack_extras=True, extras_key='extras',
          _use_future_syntax=False, **extras):
    """Specify a callable to be run after the decorated resource

    A callable provided to this decorator will be called
    any time the decorated function is executed, immediately after
    its execution.

    If the callable returns a value, that value will replace the
    return value of the decorated function.

    By default, the provided callable is called with the return from
    the decorated function as its first argument and only any
    keyword arguments provided as extras to the decoration call::

        (decorated_result, **extras)

    However, this is configurable. If all possible ``pass``
    parameters are True, the call signature would look like this::

        (decorated_result, decorated_args,
         decorated_kwargs, decorated, **extras)

    Items that are omitted will be removed from the call signature.
    For example, specifying ``pass_params=False`` and
    ``pass_decorated=True`` would adjust the call signature to
    look like::

        (decorated_result, decorated, **extras)

    Specifying ``pass_result=False`` will prevent the result
    from being passed to the callable.

    Specifying ``pass_params=True`` will pass the arguments and
    keyword arguments (as a tuple and a dict) to the decorated
    function as the second and third arguments, respectively.

    Specifying ``pass_decorated=True`` will pass a reference
    to the decorated function as the second argument, or the
    fourth argument if ``pass_params=True``

    Any extra keyword arguments passed to the decoration call
    will by default be passed directly as keyword arguments
    to ``func``. If keyword names conflict with the passed
    function, ``unpack_extras=False`` will cause extra keyword
    arguments to be passed as a dictionary using the value
    of ``extras_key``, which defaults to ``"extras"``.

    :param Callable func:
        a callable to run after the decorated function. By default,
        it is called with the result of the decorated function as
        its only argument, but the call signature may be changed
        depending on the value of ``pass_params`` and ``pass_decorated``

    :param bool pass_result:
        (default True) if True, the return from the decorated
        function will be passed to the provided callable

    :param bool pass_params:
        (default False) if True, the arguments and keyword arguments to
        the decorated function will be passed to ``func`` as a tuple
        and a dict, respectively

    :param bool pass_decorated:
        (default False) if True, a reference to the decorated function
        will be passed to the provided ``func``

    :param bool implicit_method_decoration:
        (default True) if True, decorating a class implies decorating
        all of its methods

    :param bool instance_methods_only:
        (default False) if True, decorating a class implies decorating
        only its instance methods (not ``classmethod``- or
        ``staticmethod``- decorated methods)

    :param bool unpack_extras:
        (default True) if True, any extra keyword arguments included
        in the decorator call will be passed as keyword arguments
        to ``func``. If ``False``, extra keyword arguments will be
        passed to func as a dict assigned to the keyword argument
        corresponding to ``key``

    :param str extras_key:
        (default ``"extras"``) the key to which to assign extra
        decorator keyword arguments when ``unpack_extras`` is ``False``

    :param bool _use_future_syntax:
        (default False) if True, use the new ``Decorated`` object,
        which will become the default in version 2.0.0. If this
        parameter is True, all other parameters will be ignored
        expect for ``instance_methods_only`` and
        ``implicit_method_decoration``, a ``Decorated`` object
        will be passed to the function as its first argument,
        and any provided keyword arguments will be unpacked.

    :param **dict extras:
        any extra keyword arguments supplied to the decoration call

    :return: the decorated function/method/class
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function that returns a replacement for the original"""

        def wrapper(*args, **kwargs):
            """The function that replaces the decorated one"""

            decor = decorated

            if _use_future_syntax:
                decor = Decorated(decorated, args, kwargs)

            ret = decor(*args, **kwargs)

            fn = func

            if _use_future_syntax:
                fn = partial(fn, decor)
            else:
                if pass_result:
                    fn = partial(fn, ret)

                if pass_params:
                    fn_args = get_fn_args(decorated, args)
                    fn = partial(fn, fn_args, kwargs)

                if pass_decorated:
                    fn = partial(fn, decorated)

            if unpack_extras or _use_future_syntax:
                fkwargs = extras
            else:
                fkwargs = {extras_key: extras}

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
            unpack_extras=True, extras_key='extras',
            _use_future_syntax=False, **extras):
    """Specify a callable to be run in hte place of the decorated resource

    A callable provided to this decorator will be called any time the
    decorated function is executed. The decorated function **will not**
    be called unless the provided callable calls it.

    Whatever the provided callable returns is the return value of the
    decorated function.

    By default, the provided callable is called with the arguments
    and keyword arguments used to call the decorated function, as a
    tuple and a dict, respectively, and a reference to the decorated
    function. Any extra keyword arguments specified in the decoration
    call are also passed to the callable::

        (decorated_args, decorated_kwargs, decorated, **extras)

    Items that are omitted will be removed from the call signature.
    For example, specifying ``pass_params=False`` would adjust the
    call signature to look like::

        (decorated, **extras)

    Any extra keyword arguments passed to the decoration call
    will by default be passed directly as keyword arguments
    to ``func``. If keyword names conflict with the passed
    function, ``unpack_extras=False`` will cause extra keyword
    arguments to be passed as a dictionary using the value
    of ``extras_key``, which defaults to ``"extras"``.

    :param Callable func:
        a callable to run in place of the decorated function. By
        default, it is called the decorated function's arguments
        as a tuple, keyword arguments as a dict, and a reference
        to the decorated function

    :param bool pass_params:
        (default False) if True, the arguments and keyword arguments to
        the decorated function will be passed to ``func`` as a tuple
        and a dict, respectively

    :param bool pass_decorated:
        (default False) if True, a reference to the decorated function
        will be passed to the provided ``func``

    :param bool implicit_method_decoration:
        (default True) if True, decorating a class implies decorating
        all of its methods

    :param bool instance_methods_only:
        (default False) if True, decorating a class implies decorating
        only its instance methods (not ``classmethod``- or
        ``staticmethod``- decorated methods)

    :param bool unpack_extras:
        (default True) if True, any extra keyword arguments included
        in the decorator call will be passed as keyword arguments
        to ``func``. If ``False``, extra keyword arguments will be
        passed to func as a dict assigned to the keyword argument
        corresponding to ``key``

    :param str extras_key:
        (default ``"extras"``) the key to which to assign extra
        decorator keyword arguments when ``unpack_extras`` is ``False``

    :param bool _use_future_syntax:
        (default False) if True, use the new ``Decorated`` object,
        which will become the default in version 2.0.0. If this
        parameter is True, all other parameters will be ignored
        expect for ``instance_methods_only`` and
        ``implicit_method_decoration``, a ``Decorated`` object
        will be passed to the function as its first argument,
        and any provided keyword arguments will be unpacked.

    :param **dict extras:
        any extra keyword arguments supplied to the decoration call

    :return: the decorated function/method/class
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function that returns a replacement for the original"""

        def wrapper(*args, **kwargs):
            """The function that replaces the decorated one"""

            fn = func

            if _use_future_syntax:
                decor = Decorated(decorated, args, kwargs)
                fn = partial(fn, decor)
            else:
                if pass_params:
                    fn_args = get_fn_args(decorated, args)
                    fn = partial(fn, fn_args, kwargs)

                if pass_decorated:
                    fn = partial(fn, decorated)

            if unpack_extras or _use_future_syntax:
                fkwargs = extras
            else:
                fkwargs = {extras_key: extras}

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
             _use_future_syntax=False, extras_key='extras', **extras):
    """A decorator that combines before, after, and instead decoration

    The ``before``, ``after``, and ``instead`` decorators are all
    stackable, but this decorator provides a straightforward interface
    for combining them so that you don't have to worry about
    decorator precedence. In addition, this decorator ensures that
    ``instead`` is called *first*, so that it does not replace
    any desired calls to ``before`` or ``after``.

    This decorator takes three optional keyword arguments, ``before``,
    ``after``, and ``instead``, each of which may be any callable that
    might be provided to those decorators.

    The provided callables will be invoked with the same default
    call signature as for the individual decorators. Call signatures
    and other options may be adjusted by passing ``before_opts``,
    ``after_opts``, and ``instead_opts`` dicts to this decorator,
    which will be directly unpacked into the invocation of the
    individual decorators.

    The ``instance_methods_only`` and ``implicit_method_decoration``
    options may only be changed globally as arguments to this
    decorator, in order to avoid confusion between which decorator
    is being applied to which methods.

    You may specify decorator-specific extras in the various ``opts``
    dictionaries. In addition, any extra keyword arguments passed
    to this decorator will be passed to each of the provided
    callables. As with the individual decorators, if
    ``unpack_extras=False`` is provided, the extras will be packed
    into a dict and passed via the ``extras_key`` keyword argument.

    :param Callable before:
        a callable to run before the decorated function. By default,
        it is called with no arguments, but the call signature may
        be changed depending on the value of ``pass_params`` and
        ``pass_decorated``

    :param Callable after:
        a callable to run after the decorated function. By default,
        it is called with the result of the decorated function as
        its only argument, but the call signature may be changed
        depending on the value of ``pass_params`` and ``pass_decorated``

    :param Callable instead:
        a callable to run in place of the decorated function. By
        default, it is called the decorated function's arguments
        as a tuple, keyword arguments as a dict, and a reference
        to the decorated function

    :param dict before_opts:
        a dictionary of keyword arguments to pass to the ``before``
        decorator. See :any:`before` for supported options.

    :param dict after_opts:
        a dictionary of keyword arguments to pass to the ``after``
        decorator. See :any:`after` for supported options.

    :param dict instead_opts:
        a dictionary of keyword arguments to pass to the ``instead``
        decorator. See :any:`instead` for supported options

    :param bool implicit_method_decoration:
        (default True) if True, decorating a class implies decorating
        all of its methods. This value overrides any values set in
        the various ``opts`` dictionaries.

    :param bool instance_methods_only:
        (default False) if True, decorating a class implies decorating
        only its instance methods (not ``classmethod``- or
        ``staticmethod``- decorated methods). This value overrides
        any values set in the various ``opts`` dictionaries.

    :param bool unpack_extras:
        (default True) if True, any extra keyword arguments included
        in the decorator call will be passed as keyword arguments
        to ``func``. If ``False``, extra keyword arguments will be
        passed to func as a dict assigned to the keyword argument
        corresponding to ``key``. If provided, this value serves
        as the default for the various decorators.

    :param str extras_key:
        (default ``"extras"``) the key to which to assign extra
        decorator keyword arguments when ``unpack_extras`` is
        ``False``. If provided, this key serves as the default
        for the various decorators.

    :param bool _use_future_syntax:
        (default False) if True, use the new ``Decorated`` object,
        which will become the default in version 2.0.0. If this
        parameter is True, all other parameters will be ignored
        expect for ``instance_methods_only`` and
        ``implicit_method_decoration``, a ``Decorated`` object
        will be passed to the function as its first argument,
        and any provided keyword arguments will be unpacked.

    :param **dict extras:
        any extra keyword arguments supplied to the decoration call

    :return: the decorated function/method/class
    :rtype: Union[FunctionType,MethodType,type]
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
        # Disallow mixing of class-level functionality
        opts['implicit_method_decoration'] = implicit_method_decoration
        opts['instance_methods_only'] = instance_methods_only
        opts['_use_future_syntax'] = _use_future_syntax

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


def construct_decorator(before=None, after=None, instead=None,
                        before_opts=None, after_opts=None, instead_opts=None,
                        implicit_method_decoration=True,
                        instance_methods_only=False, unpack_extras=True,
                        _use_future_syntax=False,
                        extras_key='extras', **extras):
    """Return a custom decorator

    Options are all the same as for :any:`decorate` and are, in fact,
    passed directly to it.

    Once the decorator has been created, it can be used like any
    other decorators in this module. Passing extra keyword arguments
    during the decoration call will pass those extras to the
    provided callables, even if some default extras were already set
    when creating the decorator.

    :return: a decorator that can be used to decorate functions,
        classes, or methods
    :rtype: FunctionType
    """
    return partial(
        decorate, before=before, after=after, instead=instead,
        before_opts=before_opts, after_opts=after_opts,
        instead_opts=instead_opts,
        implicit_method_decoration=implicit_method_decoration,
        instance_methods_only=instance_methods_only,
        unpack_extras=unpack_extras, extras_key=extras_key,
        _use_future_syntax=_use_future_syntax,
        **extras
    )


def _kwargs_from_opts(opts, unpack_extras, extras_key, extras):
    kwargs = opts
    if (opts.get('unpack_extras', unpack_extras) or
            opts.get('_use_future_syntax', False)):
        kwargs.update(extras)
    else:
        key = opts.get('extras_key', extras_key)
        kwargs[key] = extras
    return kwargs
