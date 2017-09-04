Changelog
=========

1.0.0
-----

Initial release!

* ``before`` decorator - run a callback prior to the decorated function
* ``after`` decorator - run a callback after the decorated function
* ``instead`` decorator  - run a callback instead of the decorated function
* ``decorate`` decorator - specify before, after, and/or instead callbacks
  all at once
* ``construct_decorator`` function - create a reusable decorator with
  before, after, and/or instead callbacks
* ``intercept`` decorator - wrap the decorated function in a try/except,
  specifying a function with which to handle the exception and/or another
  exception to re-raise
* ``log_call`` decorator - automatically log the decorated functions's
  call signature and results


1.1.0
-----

Memoization, prep for v 2.0

* ``memoize`` decorator - memoize any callable
* ``LRUCache``, ``FIFOCache``, and ``TimedCace`` - to make the ``memoize``
  decorator more useful
* ``Decorated`` class, prep for v 2.0
* ``_use_future_syntax`` option, prepping for version 2.0


1.1.1
-----

* fixed setup to pull README once more, even in Python 2
