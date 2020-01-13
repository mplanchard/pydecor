# -*- coding: UTF-8 -*-
"""
Tests for the decorators module
"""

from __future__ import absolute_import, unicode_literals


import typing as t
from logging import getLogger
from inspect import isfunction
from sys import version_info
from time import sleep
from unittest.mock import Mock, call

import pytest

from pydecor.caches import FIFOCache, LRUCache, TimedCache
from pydecor.constants import LOG_CALL_FMT_STR
from pydecor.decorators import (
    after,
    before,
    log_call,
    construct_decorator,
    decorate,
    Decorated,
    instead,
    intercept,
    memoize,
)


class TestBefore:
    """Test generic decorators."""

    def test_before_no_ret(self):
        """A before decorator with no return does not replace inbound args."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before)
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}

    def test_before_ret(self):
        """A before decorator's return, if present, replaces inbound args."""

        tracker = []

        def to_call_before(decorated: Decorated) -> t.Tuple[tuple, dict]:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})
            return (3, 4), {}

        @before(to_call_before)
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (3, 4)}

    def test_before_receives_kwargs(self):
        """Any kwargs are passed to the callable."""

        tracker = []

        def to_call_before(decorated: Decorated, extra=None) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: (decorated.args, extra)})

        @before(to_call_before, extra="read_all_about_it")
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: ((1, 2), "read_all_about_it")}
        assert tracker[1] == {2: (1, 2)}

    def test_before_implicit_instancemethod(self):
        """Before implicitly decorates instancemethods."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before)
        class _ToDecorate:
            def to_call(self, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}

    def test_before_implicit_classmethod(self):
        """Before implicitly decorates classmethods."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before)
        class _ToDecorate:
            @classmethod
            def to_call(cls, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}

    def test_before_implicit_staticmethod(self):
        """Before implicitly decorates staticmethods."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before)
        class _ToDecorate:
            @staticmethod
            def to_call(*args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}

    def test_before_implicit_instancemethod_instace_only(self):
        """Instance methods can be decorated in isolation."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before, instance_methods_only=True)
        class _ToDecorate:
            def to_call(self, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}

    def test_before_implicit_classmethod_instance_only(self):
        """Instance methods can be decorated in isolation."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before, instance_methods_only=True)
        class _ToDecorate:
            @classmethod
            def to_call(cls, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {2: (1, 2)}

    def test_before_implicit_staticmethod_instance_only(self):
        """Instance methods can be decorated in isolation."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before, instance_methods_only=True)
        class _ToDecorate:
            @staticmethod
            def to_call(*args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {2: (1, 2)}

    def test_before_method_decorates_class_if_not_implicit(self):
        """WIthout implicit method decoration, the class init is decorated."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before, implicit_method_decoration=False)
        class _ToDecorate:
            def __init__(self):
                tracker.append({0: ()})

            def to_call(self, *args):
                tracker.append({2: args})

            @classmethod
            def to_call_cls(cls, *args):
                tracker.append({3: args})

            @staticmethod
            def to_call_static(*args):
                tracker.append({4: args})

        to_decorate = _ToDecorate()

        to_decorate.to_call(3, 4)
        to_decorate.to_call_cls(3, 4)
        to_decorate.to_call_static(3, 4)

        assert len(tracker) == 5
        assert tracker[0] == {1: ()}
        assert tracker[1] == {0: ()}
        assert tracker[2] == {2: (3, 4)}
        assert tracker[3] == {3: (3, 4)}
        assert tracker[4] == {4: (3, 4)}

    def test_before_decorates_on_class_references(self):
        """Decorating class and staticmethods applies to the class ref."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        @before(to_call_before)
        class _ToDecorate:
            @classmethod
            def to_call_cls(cls, *args):
                tracker.append({2: args})

            @staticmethod
            def to_call_static(*args):
                tracker.append({3: args})

        _ToDecorate.to_call_cls(1, 2)
        _ToDecorate.to_call_static(3, 4)

        assert len(tracker) == 4
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}
        assert tracker[2] == {1: (3, 4)}
        assert tracker[3] == {3: (3, 4)}

    def test_before_direct_method_decoration_equivalent(self):
        """Direct and implicit decoration work the same way."""

        tracker = []

        def to_call_before(decorated: Decorated) -> None:
            # Ensure this happens before the wrapped call.
            tracker.append({1: decorated.args})

        class _ToDecorate:
            @before(to_call_before)
            def to_call(self, *args):
                tracker.append({2: args})

            @classmethod
            @before(to_call_before)
            def to_call_cls(cls, *args):
                tracker.append({3: args})

            @staticmethod
            @before(to_call_before)
            def to_call_static(*args):
                tracker.append({4: args})

        _ToDecorate().to_call(1, 2)
        _ToDecorate().to_call_cls(3, 4)
        _ToDecorate().to_call_static(5, 6)

        assert len(tracker) == 6
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}
        assert tracker[2] == {1: (3, 4)}
        assert tracker[3] == {3: (3, 4)}
        assert tracker[4] == {1: (5, 6)}
        assert tracker[5] == {4: (5, 6)}


class TestAfter:
    """Test generic decorators."""

    def test_after_no_ret(self):
        """A after decorator with no return does not affect teh return value."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.result})

        @after(to_call_after)
        def to_call(*args):
            tracker.append({2: args})
            return 0

        assert to_call(1, 2) == 0

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: 0}

    def test_after_ret(self):
        """A after decorator's return, if present, replaces fn return."""

        tracker = []

        def to_call_after(decorated: Decorated) -> int:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.result})
            return 1

        @after(to_call_after)
        def to_call(*args):
            tracker.append({2: args})
            return 0

        assert to_call(1, 2) == 1

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: 0}

    def test_after_receives_kwargs(self):
        """Any kwargs are passed to the callable."""

        tracker = []

        def to_call_after(decorated: Decorated, extra=None) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: (decorated.args, extra)})

        @after(to_call_after, extra="read_all_about_it")
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: ((1, 2), "read_all_about_it")}

    def test_after_implicit_instancemethod(self):
        """Before implicitly decorates instancemethods."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after)
        class _ToDecorate:
            def to_call(self, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: (1, 2)}

    def test_after_implicit_classmethod(self):
        """Before implicitly decorates classmethods."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after)
        class _ToDecorate:
            @classmethod
            def to_call(cls, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: (1, 2)}

    def test_after_implicit_staticmethod(self):
        """Before implicitly decorates staticmethods."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after)
        class _ToDecorate:
            @staticmethod
            def to_call(*args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: (1, 2)}

    def test_after_implicit_instancemethod_instace_only(self):
        """Instance methods can be decorated in isolation."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after, instance_methods_only=True)
        class _ToDecorate:
            def to_call(self, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: (1, 2)}

    def test_after_implicit_classmethod_instance_only(self):
        """Instance methods can be decorated in isolation."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after, instance_methods_only=True)
        class _ToDecorate:
            @classmethod
            def to_call(cls, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {2: (1, 2)}

    def test_after_implicit_staticmethod_instance_only(self):
        """Instance methods can be decorated in isolation."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after, instance_methods_only=True)
        class _ToDecorate:
            @staticmethod
            def to_call(*args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {2: (1, 2)}

    def test_after_method_decorates_class_if_not_implicit(self):
        """WIthout implicit method decoration, the class init is decorated."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after, implicit_method_decoration=False)
        class _ToDecorate:
            def __init__(self):
                super().__init__()
                tracker.append({0: ()})

            def to_call(self, *args):
                tracker.append({2: args})

            @classmethod
            def to_call_cls(cls, *args):
                tracker.append({3: args})

            @staticmethod
            def to_call_static(*args):
                tracker.append({4: args})

        to_decorate = _ToDecorate()

        to_decorate.to_call(3, 4)
        to_decorate.to_call_cls(3, 4)
        to_decorate.to_call_static(3, 4)

        assert len(tracker) == 5
        assert tracker[0] == {0: ()}
        assert tracker[1] == {1: ()}
        assert tracker[2] == {2: (3, 4)}
        assert tracker[3] == {3: (3, 4)}
        assert tracker[4] == {4: (3, 4)}

    def test_after_decorates_on_class_references(self):
        """Decorating class and staticmethods applies to the class ref."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        @after(to_call_after)
        class _ToDecorate:
            @classmethod
            def to_call_cls(cls, *args):
                tracker.append({2: args})

            @staticmethod
            def to_call_static(*args):
                tracker.append({3: args})

        _ToDecorate.to_call_cls(1, 2)
        _ToDecorate.to_call_static(3, 4)

        assert len(tracker) == 4
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: (1, 2)}
        assert tracker[2] == {3: (3, 4)}
        assert tracker[3] == {1: (3, 4)}

    def test_after_direct_method_decoration_equivalent(self):
        """Direct and implicit decoration work the same way."""

        tracker = []

        def to_call_after(decorated: Decorated) -> None:
            # Ensure this happens after the wrapped call.
            tracker.append({1: decorated.args})

        class _ToDecorate:
            @after(to_call_after)
            def to_call(self, *args):
                tracker.append({2: args})

            @classmethod
            @after(to_call_after)
            def to_call_cls(cls, *args):
                tracker.append({3: args})

            @staticmethod
            @after(to_call_after)
            def to_call_static(*args):
                tracker.append({4: args})

        _ToDecorate().to_call(1, 2)
        _ToDecorate().to_call_cls(3, 4)
        _ToDecorate().to_call_static(5, 6)

        assert len(tracker) == 6
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: (1, 2)}
        assert tracker[2] == {3: (3, 4)}
        assert tracker[3] == {1: (3, 4)}
        assert tracker[4] == {4: (5, 6)}
        assert tracker[5] == {1: (5, 6)}


@pytest.mark.parametrize("decorator", [before, after, instead])
def test_extras_persistence(decorator):
    """Test the persistence across calls of extras"""

    def memo_func(_decorated, memo):
        memo.append("called")

    memo = []

    decorated = Mock(return_value=None)

    decorated.__name__ = str("decorated_mock")

    decorated = decorator(memo_func, memo=memo,)(decorated)

    for _ in range(5):
        decorated()

    assert len(memo) == 5


@pytest.mark.parametrize("decorator", [before, after, instead])
def test_extras_persistence_class(decorator):
    """Test persistence of extras when decorating a class"""

    def memo_func(_decorated, memo):
        memo.append("called")

    memo = []

    @decorator(
        memo_func, memo=memo,
    )
    class GreatClass(object):
        def awesome_method(self):
            pass

        @classmethod
        def classy_method(cls):
            pass

        @staticmethod
        def stately_method():
            pass

        @property
        def prop(self):
            return "prop"

    gc = GreatClass()

    for _ in range(2):
        gc.awesome_method()

    assert len(memo) == 2

    assert gc.prop

    for _ in range(2):
        GreatClass.classy_method()

    assert len(memo) == 4

    for _ in range(2):
        gc.classy_method()

    assert len(memo) == 6

    for _ in range(2):
        GreatClass.stately_method()

    assert len(memo) == 8

    for _ in range(2):
        gc.stately_method()

    assert len(memo) == 10


@pytest.mark.parametrize("decorator", [before, after, instead])
def test_extras_persistence_class_inst_only(decorator):
    """Test persistence of extras, instance methods only"""

    def memo_func(_decorated, memo):
        memo.append("called")

    memo = []

    @decorator(
        memo_func, instance_methods_only=True, memo=memo,
    )
    class GreatClass(object):
        def awesome_method(self):
            pass

        @classmethod
        def classy_method(cls):
            pass

        @staticmethod
        def stately_method():
            pass

        @property
        def prop(self):
            return "prop"

    gc = GreatClass()

    for _ in range(2):
        gc.awesome_method()

    assert len(memo) == 2

    for _ in range(2):
        GreatClass.classy_method()

    assert gc.prop

    assert len(memo) == 2

    for _ in range(2):
        gc.classy_method()

    assert len(memo) == 2

    for _ in range(2):
        GreatClass.stately_method()

    assert len(memo) == 2

    for _ in range(2):
        gc.stately_method()

    assert len(memo) == 2


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
        called_with = handler.call_args[0][0]
        assert isinstance(called_with, raises)

    if handler is not None and not will_catch:
        handler.assert_not_called()

    wrapped.assert_called_once_with(*(), **{})


def test_log_call():
    """Test the log_call decorator"""
    exp_logger = getLogger(__name__)
    exp_logger.debug = Mock()

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
    memoizable_calls = (
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
