# -*- coding: UTF-8 -*-
"""
Tests for the decorators module
"""

from __future__ import absolute_import, unicode_literals

try:
    from unittest.mock import Mock, call
except ImportError:
    from mock import Mock, call

from logging import getLogger
from inspect import isfunction
from sys import version_info
from time import sleep

import pytest

from pydecor.caches import FIFOCache, LRUCache, TimedCache
from pydecor.constants import LOG_CALL_FMT_STR
from pydecor.decorators import (
    after,
    before,
    log_call,
    construct_decorator,
    decorate,
    instead,
    intercept,
    memoize,
)


PY2 = version_info < (3, 0)


# Common parameters for testing decorators
# ret, kwargs, fn_args, fn_kwargs
# - ret is the return value of the function passed to the decorator
# - kwargs are the kwargs passed to the decoration call
# - fn_args are the args passed to the function
# - fn_kwargs are the kwargs passed to the function
#
# Each decorator type has a helper method, below, which determines what
# the expected call to the passed function will look like.
# Decorator-specific call logic is then tested in individual tests.
#
_base_params = (
    (None, {}, (), {}),
    ((('a', ), {'b': 'c'}), {}, ('d', ), {'e': 'f'}),
    (None, {'pow': 'bang'}, (), {}),
    ((('a', ), {'b': 'c'}), {'pow': 'bang'}, (), {}),
    (None, {'pow': 'bang', 'bop': 'smack'}, (), {}),
    (None, {'pass_decorated': True}, (), {}),
    ((('a', ), {'b': 'c'}), {'pass_decorated': True}, (), {}),
    (None, {'pass_params': False}, (), {}),
    ((('a', ), {'b': 'c'}), {'pass_params': False}, (), {}),
    (None, {'pass_params': False, 'pass_decorated': True}, (), {}),
    (None, {'pass_params': False}, ('a', ), {'b': 'c'}),
    (None, {'unpack_extras': False}, (), {}),
    ((('a', ), {'b': 'c'}), {'unpack_extras': False}, (), {}),
    (None, {'unpack_extras': False, 'pow': 'bang'}, (), {}),
    (None, {'unpack_extras': False, 'extras_key': 'boo', 'k': 'd'}, (), {}),
    (None, {}, (), {}),
    ((('a', ), {'b': 'c'}), {}, ('a', ), {'b': 'c'}),
    (None, {'pass_params': False}, (), {}),
    (None, {'pass_params': False, 'pass_decorated': False}, (), {}),
    (None, {'wowee': 'zappo'}, (), {}),
    (None, {'wowee': 'zappo', 'extras_key': 'zarblock'}, (), {}),
    (
        None,
        {'wowee': 'zappo', 'extras_key': 'zarblock', 'unpack_extras': False},
        (), {}
    ),
)


base_params = []
for i in _base_params:
    base_params.append((before, ) + i)
    base_params.append((after, ) + i)
    base_params.append((instead, ) + i)


# Extra parameter combinations mostly useful when testing class decoration
_class_params = (
    (None, {'implicit_method_decoration': False}, (), {}),
    (None, {'instance_methods_only': True}, (), {}),
    (
        None, 
        {'implicit_method_decoration': False, 'instance_methods_only': True}, 
        (), {}
    ),
    (
        None,
        {'implicit_method_decoration': True, 'instance_methods_only': False},
        (), {}
    ),
    ((('a', ), {'b': 'c'}), {'implicit_method_decoration': False}, (), {}),
    ((('a', ), {'b': 'c'}), {'instance_methods_only': True}, (), {}),
    (
        (('a', ), {'b': 'c'}),
        {'implicit_method_decoration': False, 'instance_methods_only': True},
        (), {}
    ),
    (
        (('a', ), {'b': 'c'}),
        {'implicit_method_decoration': True, 'instance_methods_only': False},
        (), {}
    ),
)

class_params = []
for i in _class_params:
    class_params.append((before, ) + i)
    class_params.append((after, ) + i)
    class_params.append((instead, ) + i)

class_params.extend(base_params)


def func_sig_before(kwargs, fn_args, fn_kwargs, decorated):
    """Return the expected signature for the decorator func"""
    exp_args = ()

    if kwargs.get('pass_params', False):
        exp_args += (fn_args, fn_kwargs)

    if kwargs.get('pass_decorated', False):
        exp_args += (decorated,)

    extras = {}

    for k, v in kwargs.items():
        if k not in instead.__code__.co_varnames:
            extras[k] = v

    exp_kwargs = {}

    if kwargs.get('unpack_extras', True):
        exp_kwargs = extras
    else:
        exp_kwargs[kwargs.get('extras_key', 'extras')] = extras

    return exp_args, exp_kwargs


def func_sig_after(kwargs, fn_args, fn_kwargs, decorated,
                   decorated_ret):
    """Return the expected signature for the decorator func"""
    exp_args = ()

    if kwargs.get('pass_result', True):
        exp_args += (decorated_ret, )

    if kwargs.get('pass_params', False):
        exp_args += (fn_args, fn_kwargs)

    if kwargs.get('pass_decorated', False):
        exp_args += (decorated, )

    extras = {}

    for k, v in kwargs.items():
        if k not in instead.__code__.co_varnames:
            extras[k] = v

    exp_kwargs = {}

    if kwargs.get('unpack_extras', True):
        exp_kwargs = extras
    else:
        exp_kwargs[kwargs.get('extras_key', 'extras')] = extras

    return exp_args, exp_kwargs


def func_sig_instead(kwargs, fn_args, fn_kwargs, decorated):
    """Return the expected signature for the decorator func"""
    exp_args = ()

    if kwargs.get('pass_params', True):
        exp_args += (fn_args, fn_kwargs)

    if kwargs.get('pass_decorated', True):
        exp_args += (decorated, )

    extras = {}

    for k, v in kwargs.items():
        if k not in instead.__code__.co_varnames:
            extras[k] = v

    exp_kwargs = {}

    if kwargs.get('unpack_extras', True):
        exp_kwargs = extras
    else:
        exp_kwargs[kwargs.get('extras_key', 'extras')] = extras

    return exp_args, exp_kwargs


func_sig_map = {
    before: func_sig_before,
    'before': func_sig_before,
    after: func_sig_after,
    'after': func_sig_after,
    instead: func_sig_instead,
    'instead': func_sig_instead,
}


@pytest.mark.parametrize('decor, ret, kwargs, fn_args, fn_kwargs', base_params)
def test_function_decoration(decor, ret, kwargs, fn_args, fn_kwargs):
    """Test the decoration of functions

    :param decor: the decorator to be used
    :param ret: the return value of the function to be passed to the
        decorator
    :param kwargs: the keyword arguments to be passed to the decorator
    :param fn_args: the arguments with which the decorated function
        will be called
    :param fn_kwargs: the kwargs with which the decorated function
        will be called
    """
    decorated_mock_return = 'billyrubin'

    func_mock = Mock(return_value=ret)
    decorated_mock = Mock(return_value=decorated_mock_return)

    func_mock.__name__ = str('func_mock')
    decorated_mock.__name__ = str('decorated_mock')

    fn = decor(func_mock, **kwargs)(decorated_mock)
    fn_ret = fn(*fn_args, **fn_kwargs)

    fn_sig_func = func_sig_map[decor]
    fn_sig_args = [kwargs, fn_args, fn_kwargs, decorated_mock]
    if decor is after:
        fn_sig_args.append(decorated_mock_return)

    exp_args, exp_kwargs = fn_sig_func(*fn_sig_args)

    func_mock.assert_called_once_with(*exp_args, **exp_kwargs)

    if decor is before:
        if ret is not None:
            assert len(ret) == 2
            args, kwargs = ret
            decorated_mock.assert_called_once_with(*args, **kwargs)
        else:
            decorated_mock.assert_called_once_with(*fn_args, **fn_kwargs)

        assert fn_ret == decorated_mock_return

    elif decor is after:
        decorated_mock.assert_called_once_with(*fn_args, **fn_kwargs)

        if ret is not None:
            assert fn_ret == ret
        else:
            assert fn_ret == decorated_mock_return

    elif decor is instead:
        decorated_mock.assert_not_called()
        assert ret == fn_ret

    else:
        assert False, 'Unexpected decorator???'


@pytest.mark.parametrize(
    'decor, ret, kwargs, fn_args, fn_kwargs', class_params
)
def test_class_decoration(decor, ret, kwargs, fn_args, fn_kwargs):
    """Test decorators when applied to a class"""
    func_mock = Mock(return_value=ret)
    decorated_return = 'wow, what a return'
    meth_mock = Mock(name='meth_mock', return_value=decorated_return)
    cls_mock = Mock(name='cls_mock', return_value=decorated_return)
    static_mock = Mock(name='static_mock', return_value=decorated_return)

    @decor(func_mock, **kwargs)
    class TheClass(object):

        def method(self, *args, **kwargs):
            return meth_mock(self, *args, **kwargs)

        @classmethod
        def cls(cls, *args, **kwargs):
            return cls_mock(cls, *args, **kwargs)

        @staticmethod
        def static(*args, **kwargs):
            return static_mock(*args, **kwargs)

    mocks = (meth_mock, cls_mock, static_mock)

    for name, mock in zip(('method', 'cls', 'static'), mocks):

        if (not kwargs.get('implicit_method_decoration', True) or
                (name != 'method' and
                     kwargs.get('instance_methods_only', False))):
            # This functionality tested elsewhere
            return

        theclass = TheClass()

        meth = getattr(theclass, name)
        meth_ret = meth(*fn_args, **fn_kwargs)

        exp_meth_args = ()

        if name == 'method':
            exp_meth_args += (theclass.__wrapped__, )
        elif name == 'cls':
            exp_meth_args += (TheClass.__wrapped__, )

        exp_meth_args += fn_args

        wrapped_meth = getattr(theclass.__wrapped__, name)

        fn_sig_func = func_sig_map[decor]
        fn_sig_args = [kwargs, fn_args, fn_kwargs, wrapped_meth]
        if decor is after:
            fn_sig_args.append(decorated_return)

        exp_args, exp_kwargs = fn_sig_func(*fn_sig_args)

        func_mock.assert_called_once_with(*exp_args, **exp_kwargs)
        func_mock.reset_mock()

        if decor is before:
            if ret is not None:
                assert len(ret) == 2
                exp_args, exp_kwargs = ret
                if name != 'static':
                    exp_args = (exp_meth_args[0], ) + exp_args
                mock.assert_called_once_with(*exp_args, **exp_kwargs)
            else:
                mock.assert_called_once_with(*exp_meth_args, **fn_kwargs)

            assert meth_ret == decorated_return

        elif decor is after:
            mock.assert_called_once_with(*exp_meth_args, **fn_kwargs)

            if ret is not None:
                assert meth_ret == ret
            else:
                assert meth_ret == decorated_return

        elif decor is instead:
            mock.assert_not_called()
            assert meth_ret == ret

        else:
            assert False, 'Unexpected decorator???'


@pytest.mark.parametrize('decor, ret, kwargs, fn_args, fn_kwargs', base_params)
def test_decorate_no_mixing(decor, ret, kwargs, fn_args, fn_kwargs,
                            pass_mock=None, decor_name=None):
    """Test the ``decorate`` decorator, one type at a time"""

    decorated_mock_return = 'Elementary'

    decor_name = decor_name or decor.__name__

    pass_mock = pass_mock or Mock(return_value=ret)

    decorated_mock = Mock(return_value=decorated_mock_return)

    pass_mock.__name__ = str('before_mock')
    decorated_mock.__name__ = str('decorated_mock')

    kwargs[decor_name] = pass_mock

    fn = decorate(**kwargs)(decorated_mock)

    fn_ret = fn(*fn_args, **fn_kwargs)

    fn_sig_func = func_sig_map[decor_name]
    fn_sig_args = [kwargs, fn_args, fn_kwargs, decorated_mock]
    if decor_name == 'after':
        fn_sig_args.append(decorated_mock_return)

    # Remove the before/after/instead key from the kwargs dict, since
    # it does not get passed from the decorator call down to the
    # before/after/instead call
    del kwargs[decor_name]

    exp_args, exp_kwargs = fn_sig_func(*fn_sig_args)

    pass_mock.assert_called_once_with(*exp_args, **exp_kwargs)

    if decor_name == 'before':
        if ret is not None:
            assert len(ret) == 2
            args, kwargs = ret
            decorated_mock.assert_called_once_with(*args, **kwargs)
        else:
            decorated_mock.assert_called_once_with(*fn_args, **fn_kwargs)

        assert fn_ret == decorated_mock_return

    elif decor_name == 'after':
        decorated_mock.assert_called_once_with(*fn_args, **fn_kwargs)

        if ret is not None:
            assert fn_ret == ret
        else:
            assert fn_ret == decorated_mock_return

    elif decor_name == 'instead':
        decorated_mock.assert_not_called()
        assert ret == fn_ret

    else:
        assert False, 'Unexpected decorator???'


@pytest.mark.parametrize('decor, ret, kwargs, fn_args, fn_kwargs', base_params)
def test_decorator_constructor_no_mixing(decor, ret, kwargs, fn_args,
                                         fn_kwargs):
    """Test that decorator-generated decorators behave as expected"""

    pass_mock = Mock(return_value=ret)

    pass_mock.__name__ = str('before_mock')

    kwargs[decor.__name__] = pass_mock

    # Make a custom generated decorator
    gen_decorator = construct_decorator(**kwargs)

    test_decorate_no_mixing(
        gen_decorator,
        ret,
        kwargs,
        fn_args,
        fn_kwargs,
        pass_mock=pass_mock,
        decor_name=decor.__name__,
    )


@pytest.mark.parametrize('decorator', [before, after, instead])
def test_direct_method_decoration(decorator):
    """Test the persistence across calls of extras"""

    inst_tracker = Mock(name='inst_tracker', return_value=None)
    cls_tracker = Mock(name='cls_tracker', return_value=None)
    static_tracker = Mock(name='static_tracker', return_value=None)

    inst_tracker.__name__ = str('inst_tracker')
    cls_tracker.__name__ = str('cls_tracker')
    static_tracker.__name__ = str('static_tracker')

    class SomeClass(object):

        @decorator(inst_tracker, pass_params=True)
        def some_method(self):
            pass

        @classmethod
        @decorator(cls_tracker, pass_params=True)
        def some_clsmethod(cls):
            pass

        @staticmethod
        @decorator(static_tracker, pass_params=True)
        def some_staticmethod():
            pass

    sc = SomeClass()

    sc.some_method(), sc.some_clsmethod(), sc.some_staticmethod()

    for mock in inst_tracker, cls_tracker, static_tracker:

        assert len(mock.mock_calls) == 1

        called_with = mock.call_args[0]

        if decorator is after:
            args, kwargs = called_with[1:3]
        else:
            args, kwargs = called_with[:2]

        assert args == ()
        assert kwargs == {}


@pytest.mark.parametrize('decorator', [before, after, instead])
def test_extras_persistence(decorator):
    """Test the persistence across calls of extras"""

    def memo_func(memo, **kwargs):
        memo.append('called')

    memo = []

    decorated = Mock(return_value=None)

    decorated.__name__ = str('decorated_mock')

    decorated = decorator(
        memo_func, pass_params=False, pass_result=False,
        pass_decorated=False, memo=memo,
    )(decorated)

    for _ in range(5):
        decorated()

    assert len(memo) == 5


@pytest.mark.parametrize('decorator', [before, after, instead])
def test_extras_persistence_class(decorator):
    """Test persistence of extras when decorating a class"""

    def memo_func(memo, **kwargs):
        memo.append('called')

    memo = []

    @decorator(memo_func, pass_params=False, pass_result=False,
               pass_decorated=False, memo=memo)
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
            return 'prop'

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


@pytest.mark.parametrize('decorator', [before, after, instead])
def test_extras_persistence_class_inst_only(decorator):
    """Test persistence of extras, instance methods only"""

    def memo_func(memo, **kwargs):
        memo.append('called')

    memo = []

    @decorator(memo_func, pass_params=False, pass_result=False,
               pass_decorated=False, instance_methods_only=True,
               memo=memo)
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
            return 'prop'

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


def test_stacking_before_after():
    """Test the stacking of before followed by after"""
    tracker = Mock(name='tracker', return_value=None)

    decorated = Mock(name='decorated', return_value='decorated')

    tracker.__name__ = str('tracker')
    decorated.__name__ = str('decorated')

    fn = before(tracker)(decorated)
    fn = after(tracker)(fn)

    fn()

    decorated.assert_called_once_with()

    assert tracker.call_count == 2
    before_call_args, before_call_kwargs = tracker.call_args_list[0]
    after_call_args, after_call_kwargs = tracker.call_args_list[1]

    assert before_call_args == ()
    assert before_call_kwargs == {}

    assert after_call_args == ('decorated', )
    assert after_call_kwargs == {}


def test_stacking_after_before():
    """Test stacking of after prior to before"""
    tracker = Mock(name='tracker', return_value=None)

    decorated = Mock(name='decorated', return_value='decorated')

    tracker.__name__ = str('tracker')
    decorated.__name__ = str('decorated')

    fn = after(tracker)(decorated)
    fn = before(tracker)(fn)

    fn()

    decorated.assert_called_once_with()

    assert tracker.call_count == 2

    # The order in which before/after are specified shouldn't matter
    before_call_args, before_call_kwargs = tracker.call_args_list[0]
    after_call_args, after_call_kwargs = tracker.call_args_list[1]

    assert before_call_args == ()
    assert before_call_kwargs == {}

    assert after_call_args == ('decorated', )
    assert after_call_kwargs == {}


@pytest.mark.parametrize('decor', [before, after])
def test_stacking_instead(decor):
    """Test stacking when instead is specified last (which is WRONG)

    Note that putting instead late in the stack WILL override
    any previous decorators!
    """
    tracker = Mock(name='tracker', return_value=None)

    decorated = Mock(name='decorated', return_value='decorated')

    tracker.__name__ = str('tracker')
    decorated.__name__ = str('decorated')

    fn = decor(tracker)(decorated)
    fn = instead(tracker)(fn)

    fn()

    decorated.assert_not_called()
    assert tracker.call_count == 1
    assert tracker.call_args[0][:2] == ((), {})
    assert isfunction(tracker.call_args[0][2])


def test_stacking_instead_before():
    """Test stacking instead prior to before

    In this case, before should run properly.
    """
    tracker = Mock(name='tracker', return_value=None)

    decorated = Mock(name='decorated', return_value='decorated')

    tracker.__name__ = str('tracker')
    decorated.__name__ = str('decorated')

    fn = instead(tracker)(decorated)
    fn = before(tracker)(fn)

    fn()

    decorated.assert_not_called()

    assert tracker.call_count == 2

    before_call_args, before_call_kwargs = tracker.call_args_list[0]
    instead_call_args, instead_call_kwargs = tracker.call_args_list[1]

    assert before_call_args == ()
    assert before_call_kwargs == {}

    assert instead_call_args == ((), {}, decorated)
    assert instead_call_kwargs == {}


def test_stacking_instead_after():
    """Test stacking instead prior to after

    In this case, after should behave properly
    """
    tracker = Mock(name='tracker', return_value=None)

    decorated = Mock(name='decorated', return_value='decorated')

    tracker.__name__ = str('tracker')
    decorated.__name__ = str('decorated')

    fn = instead(tracker)(decorated)
    fn = after(tracker)(fn)

    fn()

    decorated.assert_not_called()

    assert tracker.call_count == 2

    instead_call_args, instead_call_kwargs = tracker.call_args_list[0]
    after_call_args, after_call_kwargs = tracker.call_args_list[1]

    assert instead_call_args == ((), {}, decorated)
    assert instead_call_kwargs == {}

    assert after_call_args == (None, )
    assert after_call_kwargs == {}


def test_stacking_instead_before_after():
    """Test stacking all three decorators, instead-before-after

    As long as instead is specified first, this should work fine
    """
    tracker = Mock(name='tracker', return_value=None)

    decorated = Mock(name='decorated', return_value='decorated')

    tracker.__name__ = str('tracker')
    decorated.__name__ = str('decorated')

    fn = instead(tracker)(decorated)
    fn = before(tracker)(fn)
    fn = after(tracker)(fn)

    fn()

    decorated.assert_not_called()  # because instead() doesn't call it

    assert tracker.call_count == 3

    before_call_args, before_call_kwargs = tracker.call_args_list[0]
    instead_call_args, instead_call_kwargs = tracker.call_args_list[1]
    after_call_args, after_call_kwargs = tracker.call_args_list[2]

    assert before_call_args == ()
    assert before_call_kwargs == {}

    assert instead_call_args == ((), {}, decorated)
    assert instead_call_kwargs == {}

    assert after_call_args == (None, )
    assert after_call_kwargs == {}


def test_stacking_instead_after_before():
    """Test stacking all three decorators, instead-after-before

    This should work exactly the same as instead-before-after
    """
    tracker = Mock(name='tracker', return_value=None)

    decorated = Mock(name='decorated', return_value='decorated')

    tracker.__name__ = str('tracker')
    decorated.__name__ = str('decorated')

    fn = instead(tracker)(decorated)
    fn = after(tracker)(fn)
    fn = before(tracker)(fn)

    fn()

    decorated.assert_not_called()  # because instead() doesn't call it

    assert tracker.call_count == 3

    before_call_args, before_call_kwargs = tracker.call_args_list[0]
    instead_call_args, instead_call_kwargs = tracker.call_args_list[1]
    after_call_args, after_call_kwargs = tracker.call_args_list[2]

    assert before_call_args == ()
    assert before_call_kwargs == {}

    assert instead_call_args == ((), {}, decorated)
    assert instead_call_kwargs == {}

    assert after_call_args == (None, )
    assert after_call_kwargs == {}


@pytest.mark.parametrize('raises, catch, reraise, include_handler', [
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
])
def test_intercept(raises, catch, reraise, include_handler):
    """Test the intercept decorator"""
    wrapped = Mock()

    wrapped.__name__ = str('wrapped')

    if raises is not None:
        wrapped.side_effect = raises

    handler = Mock(name='handler') if include_handler else None

    if handler is not None:
        handler.__name__ = str('handler')

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

    @log_call(level='debug')
    def func(*args, **kwargs):
        return 'foo'

    call_args = ('a', )
    call_kwargs = {'b': 'c'}

    call_res = func(*call_args, **call_kwargs)

    exp_msg = LOG_CALL_FMT_STR.format(
        name='func',
        args=call_args,
        kwargs=call_kwargs,
        result=call_res
    )

    exp_logger.debug.assert_called_once_with(exp_msg)


class TestMemoization:
    """Tests for memoization"""

    # (args, kwargs)
    memoizable_calls = (
        (('a', 'b'), {'c': 'd'}),
        ((['a', 'b', 'c'],), {'c': 'd'}),
        ((lambda x: 'foo',), {'c': lambda y: 'bar'}),
        (({'a': 'a'},), {'c': 'd'}),
        ((type(str('A'), (object,), {})(),), {}),
        ((), {}),
        ((1, 2, 3), {}),
    )

    @pytest.mark.parametrize('args, kwargs', memoizable_calls)
    def test_memoize_basic(self, args, kwargs):
        """Test basic use of the memoize decorator"""
        tracker = Mock(return_value='foo')

        @memoize()
        def func(*args, **kwargs):
            return tracker(args, kwargs)

        assert func(*args, **kwargs) == 'foo'
        tracker.assert_called_once_with(args, kwargs)

        assert func(*args, **kwargs) == 'foo'
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
