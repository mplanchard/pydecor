"""
Tests for the decorators module
"""

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import pytest

from pydecor.decorators import after, before, decorate, instead


before_params = [
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
]


def _before_exp_args_kwargs(kwargs, fn_args, fn_kwargs, decorated):
    """Get the expected args & kwargs to the func"""
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


@pytest.mark.parametrize('ret, kwargs, fn_args, fn_kwargs', before_params)
def test_before(ret, kwargs, fn_args, fn_kwargs):
    """Test test the ``before decorator"""
    func_mock = Mock(return_value=ret)
    decorated_mock = Mock(return_value='foo')

    fn = before(func_mock, **kwargs)(decorated_mock)
    fn_ret = fn(*fn_args, **fn_kwargs)

    exp_args, exp_kwargs = _before_exp_args_kwargs(
        kwargs, fn_args, fn_kwargs, decorated_mock
    )

    func_mock.assert_called_once_with(*exp_args, **exp_kwargs)

    if ret is not None:
        assert len(ret) == 2
        args, kwargs = ret
        decorated_mock.assert_called_once_with(*args, **kwargs)
    else:
        decorated_mock.assert_called_once_with(*fn_args, **fn_kwargs)

    assert fn_ret == 'foo'


@pytest.mark.parametrize('ret, kwargs, fn_args, fn_kwargs', before_params)
def test_before_class(ret, kwargs, fn_args, fn_kwargs):
    """Test before when applied to a class"""
    func_mock = Mock(return_value=ret)
    meth_mock = Mock(name='meth_mock')
    cls_mock = Mock(name='cls_mock')
    static_mock = Mock(name='static_mock')

    @before(func_mock, **kwargs)
    class TheClass:

        def method(self, *args, **kwargs):
            meth_mock(self, *args, **kwargs)

        @classmethod
        def cls(cls, *args, **kwargs):
            cls_mock(cls, *args, **kwargs)

        @staticmethod
        def static(*args, **kwargs):
            static_mock(*args, **kwargs)

    theclass = TheClass()

    mocks = (meth_mock, cls_mock, static_mock)

    for name, mock in zip(('method', 'cls', 'static'), mocks):
        meth = getattr(theclass, name)
        wrapped_meth = getattr(theclass.wrapped, name)

        meth(*fn_args, **fn_kwargs)

        exp_args, exp_kwargs = _before_exp_args_kwargs(
            kwargs, fn_args, fn_kwargs, wrapped_meth
        )

        func_mock.assert_called_once_with(*exp_args, **exp_kwargs)
        func_mock.reset_mock()

        exp_meth_args = ()
        if name == 'method':
            exp_meth_args += (theclass.wrapped, )
        elif name == 'cls':
            exp_meth_args += (TheClass.wrapped, )

        if ret is not None:
            assert len(ret) == 2
            exp_args, exp_kwargs = ret
            exp_meth_args += exp_args
            mock.assert_called_once_with(*exp_meth_args, **exp_kwargs)
        else:
            exp_meth_args += fn_args
            mock.assert_called_once_with(*exp_meth_args, **fn_kwargs)


def _instead_exp_args_kwargs(kwargs, fn_args, fn_kwargs, decorated):
    """Get the expected args & kwargs to the function"""
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


@pytest.mark.parametrize('ret, kwargs, fn_args, fn_kwargs', [
    (None, {}, (), {}),
    ('foo', {}, ('a', ), {'b': 'c'}),
    (None, {'pass_params': False}, (), {}),
    (None, {'pass_params': False, 'pass_decorated': False}, (), {}),
    (None, {'wowee': 'zappo'}, (), {}),
    (None, {'wowee': 'zappo', 'extras_key': 'zarblock'}, (), {}),
    (
        None,
        {'wowee': 'zappo', 'extras_key': 'zarblock', 'unpack_extras': False},
        (), {}
    ),
])
def test_instead(ret, kwargs, fn_args, fn_kwargs):
    """Test the ``instead`` decorator"""
    func_mock = Mock(return_value=ret)
    decorated_mock = Mock(return_value='foo')

    fn = instead(func_mock, **kwargs)(decorated_mock)

    fn_ret = fn(*fn_args, **fn_kwargs)

    exp_args, exp_kwargs = _instead_exp_args_kwargs(
        kwargs, fn_args, fn_kwargs, decorated_mock
    )

    func_mock.assert_called_once_with(*exp_args, **exp_kwargs)
    assert ret == fn_ret


def test_decorate():

    before_mock = Mock(return_value=None)
    decorated_mock = Mock(return_value=None)

    fn = decorate(before=before_mock)(decorated_mock)
    ret = fn('a')

    before_mock.assert_called_once_with(('a', ), {})
    assert ret is None
