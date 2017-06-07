"""
Private interface utilities for PyDecor
"""

from functools import partial
from logging import getLogger
from sys import version_info

from inspect import isfunction, ismethod


log = getLogger(__name__)


PY2 = version_info < (3, 0)


class ClassWrapper(object):
    """A generic class wrapper for decorating class functions/methods

    To be used in the context of a decorator that should percolate
    down to methods if used at the class level.

    Intended usage is to create a **new** class, for example by
    using the ``type()`` function, in which the ``wrapped``
    class attribute is replaced by a reference to the class
    being wrapped

    Usage:

    .. code:: python


        def meth_decorator(meth):
            '''The decorator that should be applied to class methods'''

            def wrapper(*args, **kwargs):
                print('performing wrapper tasks')
                func(*args, **kwargs)
                print('finished wrapper tasks')

            return wrapper


        def class_decorator(cls):
            '''Applies meth_decorator to class methods/functions'''
            wrapper = ClassWrapper.wrap(cls, meth_decorator)
            return wrapper


        @class_decorator
        class DecoratedClass:

            def automatically_decorated_method(self):
                pass

    """
    wrapped = None
    decorator = None
    decorator_kwargs = None

    def __init__(self, *args, **kwargs):
        self.wrapped = self.wrapped(*args, **kwargs)

    def __getattr__(self, item):
        """Return a wrapped method/function or a raw attr

        If the requested attribute is a method or a function
        (determined via ``inspect``), wrap it and return.

        Otherwise, just return the attribute.
        """
        attr = getattr(self.wrapped, item)

        if self.__class__.decorator_kwargs is None:
            kwargs = {}
        else:
            kwargs = self.__class__.decorator_kwargs

        if ismethod(attr) or isfunction(attr):
            if PY2:
                return self.__class__.decorator.__func__(attr, **kwargs)
            else:
                return self.__class__.decorator(attr, **kwargs)
        else:
            return attr

    @classmethod
    def wrap(cls, wrapped, decorator, decorator_kwargs=None):
        """Return a new class wrapping the passed class

        :param type wrapped: a reference to the class to be wrapped
        :param Union[FunctionType,MethodType,type] decorator:
            the decorator to apply to the
            functions and methods of the wrapped class
        :param dict decorator_kwargs: keyword arguments that should
            be passed to the inner decorator whenever it is
            used to decorate a method
        """
        return type(
            'Wrapped{}'.format(wrapped.__name__),
            (cls,),
            {
                'wrapped': wrapped,
                'decorator': decorator,
                'decorator_kwargs': decorator_kwargs,
            }
        )
