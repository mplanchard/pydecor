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

* ``before`` - run a callback before the decorated callable, optionally
  introspecting and altering the args and kwargs passed to the decorated
  function
* ``after`` - run a callback after the decorated callable, optionally
  introspecting and adjusting/replacing the return value
* ``decorate`` - allow providing ``before`` and ``after`` functions in
  one decorator rather than stacking

In addition, a function ``decorator`` will be provided, which will take
similar arguments to ``decorate`` above, but will instead return a new
decorator. Decorators created in this way will be callable at the function,
method, or the class level, with or without parameters, and will be
stackable.

Credits and Links
-----------------

* This project was started using my semi-custom `project template`_
* Tests are run with pytest_

.. _`project template`: https://github.com/mplanchard/python_skeleton
.. _pytest:
.. _`py.test`: https://docs.pytest.org/en/latest/
