"""
Tests for the decorators module
"""

from __future__ import absolute_import, unicode_literals

try:
    from unittest.mock import Mock
except ImportError:
    from mock import MagicMock, Mock

from sys import version_info

import pytest

from pydecor.decorators import after, before, decorate, instead


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

    if kwargs.get('pass_params', True):
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
    after: func_sig_after,
    instead: func_sig_instead,
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

    if PY2:
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
def test_class_decor_before(decor, ret, kwargs, fn_args, fn_kwargs):
    """Test decorators when applied to a class"""
    func_mock = Mock(return_value=ret)
    decorated_return = 'wow, what a return'
    meth_mock = Mock(name='meth_mock', return_value=decorated_return)
    cls_mock = Mock(name='cls_mock', return_value=decorated_return)
    static_mock = Mock(name='static_mock', return_value=decorated_return)

    @decor(func_mock, **kwargs)
    class TheClass:

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


def test_decorate():

    before_mock = Mock(return_value=None)
    decorated_mock = Mock(return_value=None)

    if PY2:
        before_mock.__name__ = str('before_mock')
        decorated_mock.__name__ = str('decorated_mock')

    fn = decorate(before=before_mock)(decorated_mock)
    ret = fn('a')

    before_mock.assert_called_once_with(('a', ), {})
    assert ret is None


@pytest.mark.parametrize('decorator', [before, after, instead])
def test_extras_persistence(decorator):
    """Test the persistence across calls of extras"""

    def memo_func(memo, **kwargs):
        memo.append('called')

    memo = []

    decorated = Mock(return_value=None)

    if PY2:
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
    class GreatClass:

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

    assert len(memo) == 2

    for _ in range(2):
        gc.classy_method()

    assert len(memo) == 4

    for _ in range(2):
        GreatClass.stately_method()

    assert len(memo) == 4

    for _ in range(2):
        gc.stately_method()

    assert len(memo) == 6


@pytest.mark.parametrize('decorator', [before, after, instead])
def test_extras_persistence_class_inst_only(decorator):
    """Test persistence of extras, instance methods only"""

    def memo_func(memo, **kwargs):
        memo.append('called')

    memo = []

    @decorator(memo_func, pass_params=False, pass_result=False,
               pass_decorated=False, instance_methods_only=True,
               memo=memo)
    class GreatClass:

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
