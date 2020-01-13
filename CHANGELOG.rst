Changelog
=========

2.0.0
-----

* ``export`` - register entities in a module's `__all__` list
  (thanks @Paebbels!)
* Use of ``Decorator`` class and consistent callable signature for generic
  decorators is now required
* Drop support for Python <3.6
* Move to a `src/` layout
* Lots of clarifications, typo fixes, and improvements to the docs
* Lots of development environment improvements:
  * Automatic distribution of tagged commits via PyPI (thanks @Paebbels!)
  * ``Makefile`` for a consistent interface into build operations
  * Improvements to ``tox`` configuration
  * Addition of consistent and required linting with pylint, mypy, and flake8
  * Autoformatting with ``black``

1.1.3
-----

Apparently `pythonhosted.org` has been deprecated, so I set up a
Read the Docs account and moved the documentation there.

* Uploaded README to point to new docs
* Added docs build image for funsies.

1.1.2
-----

* fixed an issue with the README

1.1.1
-----

* fixed setup to pull README once more, even in Python 2

1.1.0
-----

Memoization, prep for v 2.0

* ``memoize`` decorator - memoize any callable
* ``LRUCache``, ``FIFOCache``, and ``TimedCace`` - to make the ``memoize``
  decorator more useful
* ``Decorated`` class, prep for v 2.0
* ``_use_future_syntax`` option, prepping for version 2.0

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

