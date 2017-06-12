"""
Private interface utilities for PyDecor
"""

from __future__ import absolute_import, unicode_literals


__all__ = ('ClassWrapper', )


from functools import partial
from inspect import isclass
from logging import getLogger
from sys import version_info
from types import MethodType

from inspect import isfunction, ismethod


log = getLogger(__name__)


PY2 = version_info < (3, 0)


def get_fn_args(decorated, args):
    """Strip "self" and "cls" variables from args

    For now, this avoids assuming that the "self" variable is called
    "self" on instance methods, although if this winds up being
    problematic for edge use cases, I might move to that model
    and make it clear that instance methods for which "self"
    isn't called "self" won't have their "self" argument stripped.
    """
    fn_args = args
    decor_name = decorated.__name__

    # Check if the wrapped function is an attribute on args[0]
    if args and decor_name in dir(args[0]):

        # Check if args[0] is a class reference
        if isclass(args[0]):
            # Check if the wrapped function is a classmethod on the
            # class' class dict
            if type(args[0].__dict__[decor_name]) is classmethod:
                # The first argument is a reference to the class
                # containing the decorated function
                fn_args = args[1:]

        # Check if args[0] is a function defined on the class
        else:
            cls_dict = args[0].__class__.__dict__

            # Check if the wrapped function is a function on the class'
            # class dict (instance methods are functions on the class
            # dict, while classmethods and staticmethods are their own
            # types)
            if decor_name in cls_dict and isfunction(cls_dict[decor_name]):
                # The first argument is probably a "self" variable
                fn_args = args[1:]

    return fn_args


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
    __wrapped__ = None
    __decorator__ = None
    __decoropts__ = None

    def __init__(self, *args, **kwargs):
        self.__wrapped__ = self.__wrapped__(*args, **kwargs)

    def __getattribute__(self, item):

        if item in ('__wrapped__', '__decorator__', '__decoropts__'):
            return object.__getattribute__(self, item)

        wrapped = object.__getattribute__(self, '__wrapped__')
        attr = getattr(wrapped, item)

        if attr is None:
            raise AttributeError

        if ismethod(attr) or isfunction(attr):
            cls = object.__getattribute__(self, '__class__')
            decoropts = object.__getattribute__(cls, '__decoropts__')
            decor = object.__getattribute__(cls, '__decorator__')

            if decoropts['instance_methods_only']:
                cls_attr = object.__getattribute__(cls, item)
                if type(cls_attr) is classmethod:
                    return attr
                if type(cls_attr) is staticmethod:
                    return attr

            return decor(attr)

        return attr

    @classmethod
    def _get_class_attrs(cls, wrapped, decorator, instance_methods_only):
        """Get the attrs for a new class instance

        :param type wrapped: a reference to the class to be wrapped
        :param Union[FunctionType,MethodType,type] decorator:
            the decorator to apply to the
            functions and methods of the wrapped class
        """
        attrs = {}

        for k, v in wrapped.__dict__.items():
            if not k.startswith('__'):
                if not instance_methods_only:
                    if type(v) is classmethod:
                        attrs[k] = partial(decorator(v.__func__), wrapped)
                    elif type(v) is staticmethod:
                        if PY2:
                            attrs[k] = staticmethod(
                                partial(decorator(v.__func__))
                            )
                        else:
                            attrs[k] = decorator(v.__func__)
                    else:
                        attrs[k] = v
                else:
                    attrs[k] = v

        attrs.update(
            {
                '__wrapped__': wrapped,
                '__decorator__': decorator,
                '__decoropts__': {
                    'instance_methods_only': instance_methods_only
                }
            }
        )

        return attrs

    @classmethod
    def wrap(cls, wrapped, decorator, instance_methods_only=False):
        """Return a new class wrapping the passed class

        :param type wrapped: a reference to the class to be wrapped
        :param Union[FunctionType,MethodType,type] decorator:
            the decorator to apply to the
            functions and methods of the wrapped class
        """
        name = 'Wrapped{}'.format(wrapped.__name__)
        if PY2:
            name = str(name)

        return type(
            name,
            (cls, ),
            # {'__decorator__': decorator}
            cls._get_class_attrs(wrapped, decorator, instance_methods_only)
        )
