"""
Tests for the decorators module
"""

import pytest

from pydecor.decorators import after, before


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


def unpacked_with_result(func_args, func_kwargs, result):
    """Raise an assertion to ensure this is called"""
    raise RuntimeError


def unpacked_with_result_and_kwarg(func_args, func_kwargs, result,
                                   foo=None):
    """Raises an assertion if 'foo' provided"""
    if foo is not None:
        raise RuntimeError


def packed_with_result(func_args, func_kwargs, result,
                       decorator_kwargs=None):
    return packed_callback(
        func_args, func_kwargs, decorator_kwargs=decorator_kwargs)


class TestCallbacks:
    """Tests decorators that just make callbacks"""

    @pytest.mark.parametrize('decor, func, kwargs, raises', [
        (before, unpacked_callback, {}, RuntimeError),
        (before, unpacked_callback, {'foo': 'bar'}, TypeError),
        (before, unpacked_with_kwarg, {}, None),
        (before, unpacked_with_kwarg, {'foo': 'bar'}, RuntimeError),
        (before, unpacked_with_kwarg, {'foo': 'baz'}, RuntimeError),
        (after, unpacked_with_result, {}, RuntimeError),
        (after, unpacked_with_result, {'foo': 'bar'}, TypeError),
        (after, unpacked_with_result_and_kwarg, {}, None),
        (
            after,
            unpacked_with_result_and_kwarg,
            {'foo': 'bar'},
            RuntimeError
        ),
        (
            after,
            unpacked_callback,
            {'with_result': False},
            RuntimeError
        ),
        (
            after,
            unpacked_callback,
            {'foo': 'bar', 'with_result': False},
            TypeError
        ),
        (
            after,
            unpacked_with_kwarg,
            {'with_result': False},
            None
        ),
        (
            after,
            unpacked_with_kwarg,
            {'foo': 'bar', 'with_result': False},
            RuntimeError
        ),
        (
            after,
            unpacked_with_kwarg,
            {'foo': 'baz', 'with_result': False},
            RuntimeError
        ),
    ])
    def test_unpacked(self, decor, func, kwargs, raises):
        """Simple before test"""

        @decor(func, **kwargs)
        def some_func():
            return 'foo'

        if raises is not None:
            with pytest.raises(raises):
                some_func()
        else:
            assert some_func() == 'foo'

    @pytest.mark.parametrize('decor, func, kwargs, raises', [
        (before, packed_callback, {}, None),
        (before, packed_callback, {'foo': 'bar'}, RuntimeError),
        (after, packed_with_result, {}, None),
        (after, packed_with_result, {'foo': 'bar'}, RuntimeError),
    ])
    def test_packed(self, decor, func, kwargs, raises):
        """Simple before test"""

        @decor(func, unpack=False, **kwargs)
        def some_func():
            return 'foo'

        if raises is not None:
            with pytest.raises(raises):
                some_func()
        else:
            assert some_func() == 'foo'


class TestAlterations:
    """Test decorators that alter decorated params or results"""

    def test_arg_replacement(self):
        """Test replacing the decorated function args & kwargs"""

        def replacer(func_args, func_kwargs):
            return ('pining', ), {'for': 'fjords'}

        @before(replacer)
        def returner(*args, **kwargs):
            return args, kwargs

        assert returner(1, foo='bar') == (('pining', ), {'for': 'fjords'})

    def test_res_replacement(self):
        """Test replacing the return"""

        def replacer(func_args, func_kwargs, res):
            """Replace res with something else"""
            return 'belly'

        @after(replacer)
        def usurped():
            return 'flop'

        assert usurped() == 'belly'
