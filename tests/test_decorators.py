"""
Tests for the decorators module
"""

import pytest

from pydecor.decorators import before


def unpacked_callback(func_args, func_kwargs):
    """Raise an assertion to ensure this is called"""
    raise RuntimeError


def unpacked_with_kwarg(func_args, func_kwargs, foo=None):
    """Raise an assertion if foo is not None"""
    if foo is not None:
        raise RuntimeError


def packed_callback(func_args, func_kwargs, decorator_kwargs=None):
    """Raise an assertion if 'foo' in decorator_kwargs"""
    if decorator_kwargs is None:
        # This should always be populated with {} for packed calls
        raise TypeError

    if 'foo' in decorator_kwargs:
        raise RuntimeError


@pytest.mark.parametrize('func, kwargs, raises', [
    (unpacked_callback, {}, RuntimeError),
    (unpacked_callback, {'foo': 'bar'}, TypeError),
    (unpacked_with_kwarg, {}, None),
    (unpacked_with_kwarg, {'foo': 'bar'}, RuntimeError),
])
def test_before_unpacked(func, kwargs, raises):
    """Simple before test"""

    @before(func, **kwargs)
    def some_func():
        pass

    if raises is not None:
        with pytest.raises(raises):
            some_func()
    else:
        some_func()


@pytest.mark.parametrize('func, kwargs, raises', [
    (packed_callback, {}, None),
    (packed_callback, {'foo': 'bar'}, RuntimeError),
])
def test_before_packed(func, kwargs, raises):
    """Simple before test"""

    @before(func, unpack=False, **kwargs)
    def some_func():
        pass

    if raises is not None:
        with pytest.raises(raises):
            some_func()
    else:
        some_func()
