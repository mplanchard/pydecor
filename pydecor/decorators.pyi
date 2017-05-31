"""
Type hints for the decorators module
"""

from types import FunctionType, MethodType
from typing import Any, Callable, Dict, Optional, Tuple, Union


DecoratorType = Union[FunctionType, MethodType, type]
BeforeFuncReturn = Optional[Tuple[Tuple, Dict]]


def before(
        func: Callable[..., BeforeFuncReturn],
        unpack_kwargs: bool,
        **decorator_kwargs) -> DecoratorType: ...
