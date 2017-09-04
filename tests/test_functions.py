# -*- coding: UTF-8 -*-
"""
Tests for the functions module
"""

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from functools import partial
from logging import getLogger


import pytest


from pydecor.decorators import Decorated
from pydecor.constants import LOG_CALL_FMT_STR
from pydecor.functions import (
    intercept,
    log_call
)


@pytest.mark.parametrize('raises, catch, reraise, include_handler', [
    (Exception, Exception, ValueError, False),
    (Exception, Exception, ValueError, True),
    (None, Exception, ValueError, False),
    (None, Exception, ValueError, True),
    (Exception, Exception, None, False),
    (Exception, Exception, None, True),
    (Exception, RuntimeError, ValueError, False),  # won't catch
    (Exception, RuntimeError, ValueError, True),  # won't catch
])
def test_interceptor(raises, catch, reraise, include_handler):
    """Test the intercept function"""
    wrapped = Mock()
    wrapped.__name__ = 'intercept_mock'
    if raises is not None:
        wrapped.side_effect = raises

    handler = Mock() if include_handler else None

    decorated = Decorated(wrapped, (), {})

    fn = partial(intercept, decorated, catch=catch, reraise=reraise,
                 handler=handler)

    will_catch = raises and issubclass(raises, catch)

    if reraise and will_catch:
        with pytest.raises(reraise):
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
    """Test automatic logging"""
    exp_logger = getLogger(__name__)
    exp_logger.debug = Mock()

    def func(*args, **kwargs):
        return 'foo'

    call_args = ('a', )
    call_kwargs = {'b': 'c'}
    decorated = Decorated(func, call_args, call_kwargs)
    call_res = decorated(*decorated.args, **decorated.kwargs)

    log_call(decorated, level='debug')

    exp_msg = LOG_CALL_FMT_STR.format(
        name='func',
        args=call_args,
        kwargs=call_kwargs,
        result=call_res
    )

    exp_logger.debug.assert_called_once_with(exp_msg)
