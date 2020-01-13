# -*- coding: UTF-8 -*-
"""
Tests for the decorators module
"""

from __future__ import absolute_import, unicode_literals


import typing as t
from unittest.mock import Mock

import pytest

from pydecor.decorators import (
    after,
    before,
    construct_decorator,
    decorate,
    Decorated,
    instead,
)


class TestDecorated:
    """Test the Decorated wrapper."""

    def test_str(self):
        """The __name__ is included in the string."""
        assert "TestDecorated" in str(Decorated(self.__class__, (), {}))

    def test_call(self):
        """Calling gets the original result."""
        assert Decorated(lambda: 1, (), {})() == 1

    def test_call_sets_result(self):
        """Calling gets the original result."""
        decorated = Decorated(lambda: 1, (), {})
        assert decorated() == 1
        assert decorated.result == 1

    def test_immutable(self):
        """Decorated objects are immutable."""
        with pytest.raises(AttributeError):
            Decorated(lambda: None, (), {}).result = "bar"


class TestBefore:
    """Test generic decorators."""

    def test_before_no_ret(self):
        """A before decorator with no return does not replace inbound args."""

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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
        """Without implicit method decoration, the class init is decorated."""

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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
        """Without implicit method decoration, the class init is decorated."""

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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

        tracker: t.List[dict] = []

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


class TestInstead:
    """Test generic decorators."""

    def test_instead_no_call(self):
        """A instead decorator is called in place of the decorated fn."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> int:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})
            return 1

        @instead(to_call_instead)
        def to_call(*args):
            tracker.append({2: args})
            return 0

        assert to_call(1, 2) == 1

        assert len(tracker) == 1
        assert tracker[0] == {1: (1, 2)}

    def test_instead_calls(self):
        """The decorated function must be called manually."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> int:
            # Ensure this happens instead the wrapped call.
            decorated(*decorated.args, **decorated.kwargs)
            tracker.append({1: decorated.result})
            return 1

        @instead(to_call_instead)
        def to_call(*args):
            tracker.append({2: args})
            return 0

        assert to_call(1, 2) == 1

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: 0}

    def test_instead_receives_kwargs(self):
        """Any kwargs are passed to the callable."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated, extra=None) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: (decorated.args, extra)})

        @instead(to_call_instead, extra="read_all_about_it")
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {1: ((1, 2), "read_all_about_it")}

    def test_instead_implicit_instancemethod(self):
        """Before implicitly decorates instancemethods."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        @instead(to_call_instead)
        class _ToDecorate:
            def to_call(self, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {1: (1, 2)}

    def test_instead_implicit_classmethod(self):
        """Before implicitly decorates classmethods."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        @instead(to_call_instead)
        class _ToDecorate:
            @classmethod
            def to_call(cls, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {1: (1, 2)}

    def test_instead_implicit_staticmethod(self):
        """Before implicitly decorates staticmethods."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        @instead(to_call_instead)
        class _ToDecorate:
            @staticmethod
            def to_call(*args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {1: (1, 2)}

    def test_instead_implicit_instancemethod_instace_only(self):
        """Instance methods can be decorated in isolation."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        @instead(to_call_instead, instance_methods_only=True)
        class _ToDecorate:
            def to_call(self, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {1: (1, 2)}

    def test_instead_implicit_classmethod_instance_only(self):
        """Instance methods can be decorated in isolation."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        @instead(to_call_instead, instance_methods_only=True)
        class _ToDecorate:
            @classmethod
            def to_call(cls, *args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {2: (1, 2)}

    def test_instead_implicit_staticmethod_instance_only(self):
        """Instance methods can be decorated in isolation."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        @instead(to_call_instead, instance_methods_only=True)
        class _ToDecorate:
            @staticmethod
            def to_call(*args):
                tracker.append({2: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {2: (1, 2)}

    def test_instead_method_decorates_class_if_not_implicit(self):
        """Without implicit method decoration, the class init is decorated."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> t.Any:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})
            return decorated(*decorated.args, **decorated.kwargs)

        @instead(to_call_instead, implicit_method_decoration=False)
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
        assert tracker[0] == {1: ()}
        assert tracker[1] == {0: ()}
        assert tracker[2] == {2: (3, 4)}
        assert tracker[3] == {3: (3, 4)}
        assert tracker[4] == {4: (3, 4)}

    def test_instead_decorates_on_class_references(self):
        """Decorating class and staticmethods applies to the class ref."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        @instead(to_call_instead)
        class _ToDecorate:
            @classmethod
            def to_call_cls(cls, *args):
                tracker.append({2: args})

            @staticmethod
            def to_call_static(*args):
                tracker.append({3: args})

        _ToDecorate.to_call_cls(1, 2)
        _ToDecorate.to_call_static(3, 4)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {1: (3, 4)}

    def test_instead_direct_method_decoration_equivalent(self):
        """Direct and implicit decoration work the same way."""

        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated) -> None:
            # Ensure this happens instead the wrapped call.
            tracker.append({1: decorated.args})

        class _ToDecorate:
            @instead(to_call_instead)
            def to_call(self, *args):
                tracker.append({2: args})

            @classmethod
            @instead(to_call_instead)
            def to_call_cls(cls, *args):
                tracker.append({3: args})

            @staticmethod
            @instead(to_call_instead)
            def to_call_static(*args):
                tracker.append({4: args})

        _ToDecorate().to_call(1, 2)
        _ToDecorate().to_call_cls(3, 4)
        _ToDecorate().to_call_static(5, 6)

        assert len(tracker) == 3
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {1: (3, 4)}
        assert tracker[2] == {1: (5, 6)}


class TestDecorator:
    """Test the generic before/after/instead decorator."""

    def test_all_decorators(self):
        """Test adding one of each decorator type."""

        tracker: t.List[dict] = []

        def to_call_before(decorated: Decorated):
            tracker.append({1: decorated.args})

        def to_call_after(decorated: Decorated):
            tracker.append({2: decorated.args})

        def to_call_instead(decorated: Decorated):
            tracker.append({3: decorated.args})
            return decorated(*decorated.args, **decorated.kwargs)

        @decorate(
            before=to_call_before, after=to_call_after, instead=to_call_instead
        )
        def to_call(*args):
            tracker.append({4: args})

        to_call(1, 2)

        assert len(tracker) == 4
        assert tracker[0] == {1: (1, 2)}  # before
        assert tracker[1] == {3: (1, 2)}  # instead
        assert tracker[2] == {4: (1, 2)}  # wrapped
        assert tracker[3] == {2: (1, 2)}  # after

    def test_all_decorators_constructed(self):
        """A decorator can be "pre-made" if needed"""

        tracker: t.List[dict] = []

        def to_call_before(decorated: Decorated):
            tracker.append({1: decorated.args})

        def to_call_after(decorated: Decorated):
            tracker.append({2: decorated.args})

        def to_call_instead(decorated: Decorated):
            tracker.append({3: decorated.args})
            return decorated(*decorated.args, **decorated.kwargs)

        pre_made = construct_decorator(
            before=to_call_before, after=to_call_after, instead=to_call_instead
        )

        @pre_made()
        def to_call(*args):
            tracker.append({4: args})

        to_call(1, 2)

        assert len(tracker) == 4
        assert tracker[0] == {1: (1, 2)}  # before
        assert tracker[1] == {3: (1, 2)}  # instead
        assert tracker[2] == {4: (1, 2)}  # wrapped
        assert tracker[3] == {2: (1, 2)}  # after

    def test_all_callables_get_extras(self):
        """All of the callables get extra kwargs."""

        tracker: t.List[dict] = []

        def to_call_before(decorated: Decorated, kwarg=None):
            tracker.append({1: kwarg})

        def to_call_after(decorated: Decorated, kwarg=None):
            tracker.append({2: kwarg})

        def to_call_instead(decorated: Decorated, kwarg=None):
            tracker.append({3: kwarg})
            return decorated(*decorated.args, **decorated.kwargs)

        @decorate(
            before=to_call_before,
            after=to_call_after,
            instead=to_call_instead,
            kwarg=0,
        )
        def to_call(*args):
            tracker.append({4: args})

        to_call(1, 2)

        assert len(tracker) == 4
        assert tracker[0] == {1: 0}  # before
        assert tracker[1] == {3: 0}  # instead
        assert tracker[2] == {4: (1, 2)}  # wrapped
        assert tracker[3] == {2: 0}  # after

    def test_all_callables_get_specific_extras(self):
        """Specific extras are passed appropriately."""

        tracker: t.List[dict] = []

        def to_call_before(decorated: Decorated, kwarg=None):
            tracker.append({1: kwarg})

        def to_call_after(decorated: Decorated, kwarg=None):
            tracker.append({2: kwarg})

        def to_call_instead(decorated: Decorated, kwarg=None):
            tracker.append({3: kwarg})
            return decorated(*decorated.args, **decorated.kwargs)

        @decorate(
            before=to_call_before,
            before_kwargs={"kwarg": 0},
            after=to_call_after,
            after_kwargs={"kwarg": 1},
            instead=to_call_instead,
            instead_kwargs={"kwarg": 2},
        )
        def to_call(*args):
            tracker.append({4: args})

        to_call(1, 2)

        assert len(tracker) == 4
        assert tracker[0] == {1: 0}  # before
        assert tracker[1] == {3: 2}  # instead
        assert tracker[2] == {4: (1, 2)}  # wrapped
        assert tracker[3] == {2: 1}  # after

    def test_all_callables_specific_extras_overridden(self):
        """General kwargs override specific ones."""

        tracker: t.List[dict] = []

        def to_call_before(decorated: Decorated, kwarg=None):
            tracker.append({1: kwarg})

        def to_call_after(decorated: Decorated, kwarg=None):
            tracker.append({2: kwarg})

        def to_call_instead(decorated: Decorated, kwarg=None):
            tracker.append({3: kwarg})
            return decorated(*decorated.args, **decorated.kwargs)

        @decorate(
            before=to_call_before,
            before_kwargs={"kwarg": 0},
            after=to_call_after,
            after_kwargs={"kwarg": 1},
            instead=to_call_instead,
            instead_kwargs={"kwarg": 2},
            kwarg=3,
        )
        def to_call(*args):
            tracker.append({4: args})

        to_call(1, 2)

        assert len(tracker) == 4
        assert tracker[0] == {1: 3}  # before
        assert tracker[1] == {3: 3}  # instead
        assert tracker[2] == {4: (1, 2)}  # wrapped
        assert tracker[3] == {2: 3}  # after

    def test_just_before(self):
        """Test adding just before()."""
        tracker: t.List[dict] = []

        def to_call_before(decorated: Decorated):
            tracker.append({1: decorated.args})

        @decorate(before=to_call_before)
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {1: (1, 2)}
        assert tracker[1] == {2: (1, 2)}

    def test_just_after(self):
        """Test adding just after()."""
        tracker: t.List[dict] = []

        def to_call_after(decorated: Decorated):
            tracker.append({1: decorated.args})

        @decorate(after=to_call_after)
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 2
        assert tracker[0] == {2: (1, 2)}
        assert tracker[1] == {1: (1, 2)}

    def test_just_instead(self):
        """Test adding just instead()."""
        tracker: t.List[dict] = []

        def to_call_instead(decorated: Decorated):
            tracker.append({1: decorated.args})

        @decorate(instead=to_call_instead)
        def to_call(*args):
            tracker.append({2: args})

        to_call(1, 2)

        assert len(tracker) == 1
        assert tracker[0] == {1: (1, 2)}

    def test_all_decorators_implicit_class(self):
        """Test adding one of each decorator type to a class."""

        tracker: t.List[dict] = []

        def to_call_before(decorated: Decorated):
            tracker.append({1: decorated.args})

        def to_call_after(decorated: Decorated):
            tracker.append({2: decorated.args})

        def to_call_instead(decorated: Decorated):
            tracker.append({3: decorated.args})
            return decorated(*decorated.args, **decorated.kwargs)

        @decorate(
            before=to_call_before, after=to_call_after, instead=to_call_instead
        )
        class _ToDecorate:
            def to_call(self, *args):
                tracker.append({4: args})

        _ToDecorate().to_call(1, 2)

        assert len(tracker) == 4
        assert tracker[0] == {1: (1, 2)}  # before
        assert tracker[1] == {3: (1, 2)}  # instead
        assert tracker[2] == {4: (1, 2)}  # wrapped
        assert tracker[3] == {2: (1, 2)}  # after

    def test_at_least_one_callable_must_be_specified(self):
        """Not specifying any callables does not work."""
        with pytest.raises(ValueError):

            @decorate()
            def _fn():
                pass


@pytest.mark.parametrize("decorator", [before, after, instead])
def test_extras_persistence(decorator):
    """Test the persistence across calls of extras"""

    def memo_func(_decorated, memo):
        memo.append("called")

    memo: list = []

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

    memo: list = []

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

    memo: list = []

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
