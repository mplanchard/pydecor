"""
A module housing the decorators provided in the public API of PyDecor
"""

from __future__ import absolute_import, unicode_literals


__all__ = (
    'after',
    'before',
    'decorate',
    'instead',
    'intercept',
    'log_call',
    'DecoratorType',
)


from inspect import isclass
from logging import getLogger
from functools import partial, wraps
from types import FunctionType, MethodType
from typing import Union

from . import functions
from ._util import ClassWrapper, get_fn_args
from .constants import LOG_CALL_FMT_STR

log = getLogger(__name__)


DecoratorType = Union[FunctionType, MethodType, type]


def before(func, pass_params=False, pass_decorated=False,
           implicit_method_decoration=True, instance_methods_only=False,
           unpack_extras=True, extras_key='extras', **extras):
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

    :param **dict extras:
        any extra keyword arguments supplied to the decoration call
    
    :return: the decorated function/method/class
    :rtype: Union[FunctionType,MethodType,type]
    """

    def decorator(decorated):
        """The function that returns a replacement for the original"""

        def wrapper(*args, **kwargs):
            """The function that replaces the decorated one"""

            fkwargs = extras if unpack_extras else {extras_key: extras}

            fn = func

            if pass_params:
                fn_args = get_fn_args(decorated, args)
                fn = partial(fn, fn_args, kwargs)

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

    :param **dict extras:
        any extra keyword arguments supplied to the decoration call

    :return: the decorated function/method/class
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
                fn_args = get_fn_args(decorated, args)
                fn = partial(fn, fn_args, kwargs)

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

            if pass_params:
                fn_args = get_fn_args(decorated, args)
                fn = partial(fn, fn_args, kwargs)

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
        **extras
    )


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
        catch=catch,
        reraise=reraise,
        handler=handler,
        err_msg=err_msg,
        include_context=include_context
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
        pass_params=True,
        pass_decorated=True,
        logger=logger,
        level=level,
        format_str=format_str
    )


def _kwargs_from_opts(opts, unpack_extras, extras_key, extras):
    kwargs = opts
    if opts.get('unpack_extras', unpack_extras):
        kwargs.update(extras)
    else:
        key = opts.get('extras_key', extras_key)
        kwargs[key] = extras
    return kwargs
