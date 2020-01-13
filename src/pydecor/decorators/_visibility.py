# EMACS settings: -*- coding: utf-8 -*-
"""
Decorators controlling visibility of entities in a Python module.
"""

__all__ = ("export",)
__api__ = __all__

import sys
import typing as t


T = t.TypeVar("T", bound=t.Callable)


def export(entity: T) -> T:
    """Register the given function or class as publicly accessible in a module.

    Creates or updates the `__all__` attribute in the module in which the
    decorated entity is defined to include the name of the decorated
    entity.

    Example:

    `to_export.py`:

    .. code:: python

        from pydecor import export

        @export
        def exported():
            pass

        def not_exported():
            pass


    `another_file.py`

    .. code:: python

        from .to_export import *

        assert "exported" in globals()
        assert "not_exported" not in globals()


    :param Union[Type, types.FunctionType] entity: the function or class
        to include in `__all__`
    """
    # * Based on an idea by Duncan Booth:
    #   http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
    # * Improved via a suggestion by Dave Angel:
    #   http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1

    if not hasattr(entity, "__module__"):
        raise TypeError(
            (
                "{entity} has no __module__ attribute. Please ensure it is "
                "a top-level function or class reference defined in a module."
            ).format(entity=entity)
        )

    if hasattr(entity, "__qualname__"):
        if any(i in entity.__qualname__ for i in (".", "<locals>", "<lambda>")):
            raise TypeError(
                "Only named top-level functions and classes may be exported, "
                "not {}".format(entity)
            )

    if not hasattr(entity, "__name__") or entity.__name__ == "<lambda>":
        raise TypeError(
            "Entity must be a named top-level funcion or class, not {}".format(
                type(entity)
            )
        )

    try:
        module = sys.modules[entity.__module__]
    except KeyError:
        raise ValueError(
            (
                "Module {} is not present in sys.modules. Please ensure "
                "it is in the import path before calling export()."
            ).format(entity.__module__)
        )
    if hasattr(module, "__all__"):
        if entity.__name__ not in module.__all__:  # type: ignore
            module.__all__ = module.__all__.__class__(  # type: ignore
                (*module.__all__, entity.__name__)  # type: ignore
            )
    else:
        module.__all__ = [entity.__name__]  # type: ignore

    return entity
