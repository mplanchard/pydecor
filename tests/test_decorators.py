"""
Tests for the decorators module
"""

import pytest

from pydecor.decorators import after, before


def generic_func(*args, **kwargs):
    """Just return the call params"""
    print('generic_func(*{}, **{})'.format(args, kwargs))
    return args, kwargs


def null_return(*args, **kwargs):
    """Return None"""
    print('null_return(*{}, **{})'.format(args, kwargs))
    return None


@pytest.mark.parametrize(
    'wrapped, passed, dec_kwargs, func_args, func_kwargs, exp_ret', [
        (   # All defaults, no params
            generic_func,
            null_return,
            {},
            (),
            {},
            ((), {})
        ),
        (   # General case, parameters not adjustment
            generic_func,
            null_return,
            {},
            ('a', 'b'),
            {'foo': 'bar'},
            (('a', 'b'), {'foo': 'bar'})
        ),
        (   # General case, parameters not adjustment, extra kwargs
            generic_func,
            null_return,
            {'extra': 'wow!'},
            ('a', 'b'),
            {'foo': 'bar'},
            (('a', 'b'), {'foo': 'bar'})
        ),
        (   # Case where parameters are replaced
            generic_func,
            generic_func,
            {},
            ('a', ),
            {'foo': 'bar'},
            ((('a', ), {'foo': 'bar'}), {})
        ),
        (   # Case where parameters are replaced, and a decorator
            # kwarg is passed to the passed function
            generic_func,
            generic_func,
            {'decorators': 'cool'},
            ('a', ),
            {'foo': 'bar'},
            ((('a', ), {'foo': 'bar'}), {'decorators': 'cool'})
        ),
        (   # Case where parameters are replaced, and a decorator
            # kwarg is passed to the passed function, but the
            # passed_kwargs are not unpacked
            generic_func,
            generic_func,
            {'decorators': 'cool', 'unpack_passed': False},
            ('a', ),
            {'foo': 'bar'}, (
                (('a', ), {'foo': 'bar'}),
                {'passed': {'decorators': 'cool'}}
            )
        ),
        (   # Case where parameters are replaced, and a decorator
            # kwarg is passed to the passed function, but the
            # passed_kwargs are not unpacked, and a custom key
            # is specified
            generic_func,
            generic_func, {
                'decorators': 'cool',
                'unpack_passed': False,
                'passed_key': 'cool_kwargs'
            },
            ('a', ),
            {'foo': 'bar'}, (
                (('a', ), {'foo': 'bar'}),
                {'cool_kwargs': {'decorators': 'cool'}}
            )
        ),
        (   # Case where parameters are replaced, but the passed
            # function doesn't get any params.
            generic_func,
            generic_func,
            {'with_params': False},
            ('a', ),
            {'foo': 'bar'},
            ((), {}),
        ),
        (   # Case where parameters are replaced, the passed function
            # gets no params, and an extra passed kwarg is specified
            generic_func,
            generic_func,
            {'with_params': False, 'extra': 'woo'},
            ('a', ),
            {'foo': 'bar'},
            ((), {'extra': 'woo'}),
        ),
        (   # Case where parameters are replaced, the passed
            # function gets no params, and extra kwargs are not
            # unpacked
            generic_func,
            generic_func, {
                'with_params': False,
                'extra': 'woo',
                'unpack_passed': False
            },
            ('a', ),
            {'foo': 'bar'},
            ((), {'passed': {'extra': 'woo'}}),
        ),
        (   # Case where parameters are replaced, the passed
            # function gets no params, and extra kwargs are not
            # unpacked, and a custom key is specified
            generic_func,
            generic_func, {
                'with_params': False,
                'extra': 'woo',
                'unpack_passed': False,
                'passed_key': 'wow!'
            },
            ('a', ),
            {'foo': 'bar'},
            ((), {'wow!': {'extra': 'woo'}}),
        ),
    ]
)
def test_before_decorator(wrapped, passed, dec_kwargs, func_args,
                          func_kwargs, exp_ret):
    """Test decoration with the before decorator"""
    func = before(passed, **dec_kwargs)(wrapped)
    ret = func(*func_args, **func_kwargs)
    assert ret == exp_ret


@pytest.mark.parametrize(
    'wrapped, passed, dec_kwargs, func_args, func_kwargs, exp_ret', [
        (   # Generic case, all defaults, no params
            generic_func,
            null_return,
            {},
            (),
            {},
            ((), {})
        ),
        (   # Generic case, all defaults, func params
            generic_func,
            null_return,
            {},
            ('a', ),
            {'oh': 'my'},
            (('a', ), {'oh': 'my'})
        ),
        (   # Generic case, all defaults, func params, extra kwargs
            generic_func,
            null_return,
            {'new': 'hotness'},
            ('a', ),
            {'oh': 'my'},
            (('a', ), {'oh': 'my'})
        ),
        (   # Null return wrapped, passed also returns null
            null_return,
            null_return,
            {},
            ('a', ),
            {'oh': 'my'},
            None,
        ),
        (   # Null return wrapped, replaced with passed return
            null_return,
            generic_func,
            {},
            ('a', ),
            {'oh': 'my'},
            ((None, ), {}),
        ),
        (   # Null return wrapped, replaced with passed return, extra
            # kwargs
            null_return,
            generic_func,
            {'passed': 'yeah!'},
            ('a', ),
            {'oh': 'my'},
            ((None, ), {'passed': 'yeah!'}),
        ),
        (   # Null return wrapped, replaced with passed return, extra
            # kwargs, kwargs not unpacked
            null_return,
            generic_func,
            {'passed': 'yeah!', 'unpack_passed': False},
            ('a', ),
            {'oh': 'my'},
            ((None, ), {'passed': {'passed': 'yeah!'}}),
        ),
        (   # Null return wrapped, replaced with passed return, extra
            # kwargs, kwargs not unpacked, custom key
            null_return,
            generic_func,
            {'passed': 'yeah!', 'unpack_passed': False, 'passed_key': 'a'},
            ('a', ),
            {'oh': 'my'},
            ((None, ), {'a': {'passed': 'yeah!'}}),
        ),
        (   # Null return wrapped, replaced with passed return,
            # params included with ret
            null_return,
            generic_func,
            {'with_params': True},
            ('a', ),
            {'oh': 'my'},
            ((None, ('a', ), {'oh': 'my'}), {}),
        ),
        (   # Null return wrapped, replaced with passed return,
            # params included with ret, extra kwarg
            null_return,
            generic_func,
            {'with_params': True, 'neato': 'torpedo'},
            ('a', ),
            {'oh': 'my'},
            ((None, ('a', ), {'oh': 'my'}), {'neato': 'torpedo'}),
        ),
        (   # Null return wrapped, replaced with passed return,
            # params included, result not included
            null_return,
            generic_func,
            {'with_params': True, 'with_result': False},
            ('a', ),
            {'oh': 'my'},
            ((('a', ), {'oh': 'my'}), {}),
        ),
    ]
)
def test_after_decorator(wrapped, passed, dec_kwargs, func_args,
                         func_kwargs, exp_ret):
    """Test decoration with the after decorator"""
    func = after(passed, **dec_kwargs)(wrapped)
    ret = func(*func_args, **func_kwargs)
    assert ret == exp_ret


@pytest.mark.parametrize(
    'passed, dec_kwargs, func_args, func_kwargs, exp_ret', [
        (   # Before returns nothing, called params returned
            null_return,
            {},
            ('a', ),
            {'foo': 'bar'},
            (('a', ), {'foo': 'bar'})
        ),
        (   # Before return something, params passed, params to passed
            # func returned as packed tuple/dict
            generic_func,
            {},
            ('a', ),
            {'foo': 'bar'},
            ((('a', ), {'foo': 'bar'}), {})
        ),
        (   # Before return something, params passed, params to passed
            # func returned as packed tuple/dict, extra kwargs passed
            # to the passed function & returned as its kwargs
            generic_func,
            {'extra': 'amazing!'},
            ('a', ),
            {'foo': 'bar'},
            ((('a', ), {'foo': 'bar'}), {'extra': 'amazing!'})
        ),
        (   # Before returns something, params NOT passed to it,
            # so original params are replaced with empty tuple/dict
            generic_func,
            {'with_params': False},
            ('a', ),
            {'foo': 'bar'},
            ((), {})
        ),
    ]
)
def test_before_class(passed, dec_kwargs, func_args, func_kwargs,
                      exp_ret):
    """Test that classes are successfully decorated by @before"""

    @before(passed, **dec_kwargs)
    class GreatClass(object):

        def __init__(self):
            pass

        def regular_method(self, *args, **kwargs):
            return args, kwargs

        @classmethod
        def class_method(cls, *args, **kwargs):
            return args, kwargs

        @staticmethod
        def static_method(*args, **kwargs):
            return args, kwargs

    great_class = GreatClass()

    for name in ('regular_method', 'class_method', 'static_method'):
        meth = getattr(great_class, name)
        assert meth(*func_args, **func_kwargs) == exp_ret
