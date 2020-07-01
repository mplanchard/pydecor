"""Test ready-to-use decorators."""

import typing as t
from logging import getLogger
from time import sleep
from unittest.mock import Mock, call

import pytest

from pydecor.caches import FIFOCache, LRUCache, TimedCache
from pydecor.constants import LOG_CALL_FMT_STR
from pydecor.decorators import (
    log_call,
    intercept,
    memoize,
)


@pytest.mark.parametrize(
    "raises, catch, reraise, include_handler",
    [
        (Exception, Exception, ValueError, False),
        (Exception, Exception, ValueError, True),
        (Exception, Exception, True, True),
        (Exception, Exception, True, False),
        (None, Exception, ValueError, False),
        (None, Exception, ValueError, True),
        (Exception, Exception, None, False),
        (Exception, Exception, None, True),
        (Exception, RuntimeError, ValueError, False),  # won't catch
        (Exception, RuntimeError, ValueError, True),  # won't catch
    ],
)
def test_intercept(raises, catch, reraise, include_handler):
    """Test the intercept decorator"""
    wrapped = Mock()

    wrapped.__name__ = str("wrapped")

    if raises is not None:
        wrapped.side_effect = raises

    handler = Mock(name="handler") if include_handler else None

    if handler is not None:
        handler.__name__ = str("handler")

    fn = intercept(catch=catch, reraise=reraise, handler=handler)(wrapped)

    will_catch = raises and issubclass(raises, catch)

    if reraise and will_catch:
        to_be_raised = raises if reraise is True else reraise
        with pytest.raises(to_be_raised):
            fn()
    elif raises and not will_catch:
        with pytest.raises(raises):
            fn()
    else:
        fn()

    if handler is not None and will_catch:
        # pylint: disable=unsubscriptable-object
        called_with = handler.call_args[0][0]
        # pylint: enable=unsubscriptable-object
        assert isinstance(called_with, raises)

    if handler is not None and not will_catch:
        handler.assert_not_called()

    wrapped.assert_called_once_with(*(), **{})  # type: ignore


def test_intercept_method():
    """Test decorating an instance method with intercept."""

    calls = []

    def _handler(exc):
        calls.append(exc)

    class SomeClass:
        @intercept(handler=_handler)
        def it_raises(self, val):
            raise ValueError(val)

    SomeClass().it_raises("a")
    assert len(calls) == 1
    assert isinstance(calls[0], ValueError)


def test_log_call():
    """Test the log_call decorator"""
    exp_logger = getLogger(__name__)
    exp_logger.debug = Mock()  # type: ignore

    @log_call(level="debug")
    def func(*args, **kwargs):
        return "foo"

    call_args = ("a",)
    call_kwargs = {"b": "c"}

    call_res = func(*call_args, **call_kwargs)

    exp_msg = LOG_CALL_FMT_STR.format(
        name="func", args=call_args, kwargs=call_kwargs, result=call_res
    )

    exp_logger.debug.assert_called_once_with(exp_msg)


class TestMemoization:
    """Tests for memoization"""

    # (args, kwargs)
    memoizable_calls: t.Tuple[t.Tuple, ...] = (
        (("a", "b"), {"c": "d"}),
        ((["a", "b", "c"],), {"c": "d"}),
        ((lambda x: "foo",), {"c": lambda y: "bar"}),
        (({"a": "a"},), {"c": "d"}),
        ((type(str("A"), (object,), {})(),), {}),
        ((), {}),
        ((1, 2, 3), {}),
    )

    @pytest.mark.parametrize("args, kwargs", memoizable_calls)
    def test_memoize_basic(self, args, kwargs):
        """Test basic use of the memoize decorator"""
        tracker = Mock(return_value="foo")

        @memoize()
        def func(*args, **kwargs):
            return tracker(args, kwargs)

        assert func(*args, **kwargs) == "foo"
        tracker.assert_called_once_with(args, kwargs)

        assert func(*args, **kwargs) == "foo"
        assert len(tracker.mock_calls) == 1

    def test_memoize_lru(self):
        """Test removal of least-recently-used items"""
        call_list = tuple(range(5))  # 0-4
        tracker = Mock()

        @memoize(keep=5, cache_class=LRUCache)
        def func(val):
            tracker(val)
            return val

        for val in call_list:
            func(val)

        # LRU: 0 1 2 3 4
        assert len(tracker.mock_calls) == len(call_list)
        for val in call_list:
            assert call(val) in tracker.mock_calls

        # call with all the same args
        for val in call_list:
            func(val)

        # no new calls, lru order should be same
        # LRU: 0 1 2 3 4
        assert len(tracker.mock_calls) == len(call_list)
        for val in call_list:
            assert call(val) in tracker.mock_calls

        # add new value, popping least-recently-used (0)
        # LRU: 1 2 3 4 5
        func(5)
        assert len(tracker.mock_calls) == len(call_list) + 1
        assert tracker.mock_calls[-1] == call(5)  # most recent call

        # Re-call with 0, asserting that we call the func again,
        # and dropping 1
        # LRU: 2 3 4 5 0
        func(0)
        assert len(tracker.mock_calls) == len(call_list) + 2
        assert tracker.mock_calls[-1] == call(0)  # most recent call

        # Let's ensure that using something rearranges it
        func(2)
        # LRU: 3 4 5 0 2
        # no new calls
        assert len(tracker.mock_calls) == len(call_list) + 2
        assert tracker.mock_calls[-1] == call(0)  # most recent call

        # Let's put another new value into the cache
        func(6)
        # LRU: 4 5 0 2 6
        assert len(tracker.mock_calls) == len(call_list) + 3
        assert tracker.mock_calls[-1] == call(6)

        # Assert that 2 hasn't been dropped from the list, like it
        # would have been if we hadn't called it before 6
        func(2)
        # LRU: 4 5 0 6 2
        assert len(tracker.mock_calls) == len(call_list) + 3
        assert tracker.mock_calls[-1] == call(6)

    def test_memoize_fifo(self):
        """Test using the FIFO cache"""
        call_list = tuple(range(5))  # 0-4
        tracker = Mock()

        @memoize(keep=5, cache_class=FIFOCache)
        def func(val):
            tracker(val)
            return val

        for val in call_list:
            func(val)

        # Cache: 0 1 2 3 4
        assert len(tracker.mock_calls) == len(call_list)
        for val in call_list:
            assert call(val) in tracker.mock_calls

        # call with all the same args
        for val in call_list:
            func(val)

        # no new calls, cache still the same
        # Cache: 0 1 2 3 4
        assert len(tracker.mock_calls) == len(call_list)
        for val in call_list:
            assert call(val) in tracker.mock_calls

        # add new value, popping first in (0)
        # Cache: 1 2 3 4 5
        func(5)
        assert len(tracker.mock_calls) == len(call_list) + 1
        assert tracker.mock_calls[-1] == call(5)  # most recent call

        # Assert 5 doesn't yield a new call
        func(5)
        assert len(tracker.mock_calls) == len(call_list) + 1
        assert tracker.mock_calls[-1] == call(5)  # most recent call

        # Re-call with 0, asserting that we call the func again,
        # and dropping 1
        # Cache: 2 3 4 5 0
        func(0)
        assert len(tracker.mock_calls) == len(call_list) + 2
        assert tracker.mock_calls[-1] == call(0)  # most recent call

        # Assert neither 0 nor 5 yield new calls
        func(0)
        func(5)
        assert len(tracker.mock_calls) == len(call_list) + 2
        assert tracker.mock_calls[-1] == call(0)  # most recent call

    def test_memoization_timed(self):
        """Test timed memoization"""
        time = 0.005
        tracker = Mock()

        @memoize(keep=time, cache_class=TimedCache)
        def func(val):
            tracker(val)
            return val

        assert func(1) == 1
        assert tracker.mock_calls == [call(1)]
        assert func(1) == 1
        assert tracker.mock_calls == [call(1)]
        sleep(time)
        assert func(1) == 1
        assert tracker.mock_calls == [call(1), call(1)]
