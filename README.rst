PyDecor
=======

Easy-peasy Python decorators!


Work in Progress!
-----------------

.. WARNING::
  **This is a work in progress! It is still marked as being in the
  Planning stage, and it is not ready for third-party usage. Breaking
  changes may occur, and all planned functionality is not yet present**


Summary
-------

Decorators are great, but they're hard to write, especially if you want
to include arguments to your decorators, or use your decorators on
classes as well as functions, or if you want to be able to call your
decorators with or without parentheses.

PyDecor aims to make function easy and straightforward, so that developers
can stop worrying about closures and syntax in triply nested functions and
instead get down to decorating!

Planned Featureset
------------------

My plan is to include the following callback-oriented decorators.
All decorators will be capable of functioning at the function, method, or
class level. Decorators will be stackable.

General Purpose Decorators
**************************

All planned for the ``1.0.0`` release

* ``before`` - run a callback before the decorated callable, optionally
  introspecting and altering the args and kwargs passed to the decorated
  function
* ``after`` - run a callback after the decorated callable, optionally
  introspecting and adjusting/replacing the return value
* ``instead`` - run a callback in place of the decorated callable, optionally
  introspecting the callable's arguments and receiving a reference to the
  callable itself
* ``decorate`` - allow providing ``before`` and ``after`` functions in
  one decorator rather than stacking

Decorator Constructor
*********************

For the ``1.0.0`` release

A function ``decorator`` will be provided, which will take
similar arguments to ``decorate`` above, but will instead return a new
decorator. Decorators created in this way will be callable at the function,
method, or the class level, with or without parameters, and will be
stackable.

Convenience Decorators
**********************

In addition, a few convenience decorators will be provided, constructed with
the tools defined above.

Convenience decorators will be added in the ``1.1.0`` release.

* ``log`` - automatically log the function arguments & result. Attempt
  to import the correct logger instance automatically, while optionally
  taking an explicit logger
* ``export`` - add the decorated item to ``__all__``
* ``intercept`` - intercept a list of exceptions and either raise a custom
  exception or run a callable
* ``skipif`` - similar to py.test's decorator, skip the function if a
  provided condition is True
* ``memoize`` - store function results in a local dictionary cache


Credits and Links
-----------------

* This project was started using my semi-custom `project template`_
* Tests are run with pytest_

.. _`project template`: https://github.com/mplanchard/python_skeleton
.. _pytest:
.. _`py.test`: https://docs.pytest.org/en/latest/
