"""
Tests for the functions module
"""

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from functools import partial


import pytest


from pydecor.functions import (
    interceptor,
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
    """Test the interceptor function"""
    wrapped = Mock()
    if raises is not None:
        wrapped.side_effect = raises

    handler = Mock() if include_handler else None

    fn = partial(interceptor, (), {}, wrapped, catch=catch, reraise=reraise,
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
