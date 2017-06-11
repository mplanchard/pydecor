"""
Private interface utilities for PyDecor
"""

from __future__ import absolute_import, unicode_literals


__all__ = ('ClassWrapper', )


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

            if PY2:
                return decor(attr)
            else:
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
