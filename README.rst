PyDecor
=======

Easy-peasy Python decorators!

GitHub: https://github.com/mplanchard/pydecor

PyPI: https://pypi.python.org/pypi/pydecor

Docs: https://pythonhosted.org/pydecor/


Summary
-------

Decorators are great, but they're hard to write, especially if you want
to include arguments to your decorators, or use your decorators on
class methods as well as functions. I know that, no matter how many I write,
I still find myself looking up the syntax every time. And that's just for
simple function decorators. Getting decorators to work consistently at the
class and method level is a whole 'nother barrel of worms.

PyDecor aims to make function easy and straightforward, so that developers
can stop worrying about closures and syntax in triply nested functions and
instead get down to decorating!

.. contents:: Table of Contents

Why PyDecor?
------------

* **It's easy!**

  With PyDecor, you can go from this:

  .. code:: python

    from functools import wraps
    from flask import request
    from werkzeug.exceptions import Unauthorized
    from my_pkg.auth import authorize_request

    def auth_decorator(request=None):
        """Check the passed request for authentication"""

        def decorator(decorated):

            @wraps(decorated)
            def wrapper(*args, **kwargs):
                if not authorize_request(request):
                  raise Unauthorized('Not authorized!')
                return decorated(*args, **kwargs)
            return wrapper

        return decorated

    @auth_decorator(request=requst)
    def some_view():
        return 'Hello, World!'

  to this:

  .. code:: python

    from flask import request
    from pydecor import before
    from werkzeug.exceptions import Unauthorized
    from my_pkg.auth import authorize_request

    def check_auth(request=request):
        """Ensure the request is authorized"""
        if not authorize_request(request):
          raise Unauthorized('Not authorized!')

    @before(check_auth, request=request)
    def some_view():
        return 'Hello, world!'

  Not only is it less code, but you don't have to remember decorator
  syntax or mess with nested functions. Full disclosure, I had to look
  up a decorator sample to be sure I got the first example's syntax right,
  and I just spent two weeks writing a decorator library.

* **It's fast!**

  The test suite for this library (326 tests of this writing) runs in
  about 0.88 seconds, on average. That's hundreds of decorations, plus py.test
  spinup time, plus a bunch of complicated mocking.

* **Implicit Method Decoration!**

  Getting a decorator to "roll down" to methods when applied to a class is
  a complicated business, but all of PyDecor's decorators provide it for
  free, so rather than writing:

  .. code:: python

    from pydecor import log_call

    class FullyLoggedClass(object):

        @log_call(level='debug')
        def some_function(self, *args, **kwargs):
            return args, kwargs

        @log_call(level='debug')
        def another_function(self, *args, **kwargs):
            return None

        ...

  You can just write:

  .. code:: python

    from pydecor import log_call

    @log_call(level='debug')
    class FullyLoggedClass(object):

        def some_function(self, *args, **kwargs):
            return args, kwargs

        def another_function(self, *args, **kwargs):
            return None

        ...

  PyDecor ignores special methods (like ``__init__``) so as not to interfere
  with deep Python magic. By default, it works on any methods of an instance,
  including class and static methods! It also ensures that class attributes
  are preserved after decoration, so your class references continue to behave
  as expected.

* **Consistent Method Decoration!**

  Whether you're decorating a class, an instance method, a class method, or
  a static method, you can use the same passed function. ``self`` and ``cls``
  variables are stripped out of the method parameters passed to the provided
  callable, so your functions don't need to care about where they're used.

* **Lots of Tests!**

  Seriously. Don't believe me? Just look. We've got the best tests. Just
  phenomenal.


Installation
------------

Supported Python versions are 2.7 and 3.4+

To install `pydecor`, simply run::

  pip install -U pydecor

To install the current development release::

  pip install --pre -U pydecor

You can also install from source to get the absolute most recent
code, which may or may not be functional::

  git clone https://github.com/mplanchard/pydecor
  pip install ./pydecor



Quickstart
----------

Provided Decorators
*******************

This package provides generic decorators, which can be used with any
function to provide extra utility to decorated resources, as well
as convenience decorators implemented using those generic decorators.

Generics
~~~~~~~~

* ``before`` - run a callable before the decorated function executes

  * by default called with no arguments other than extras

* ``after`` - run a callable after the decorated function executes

  * by default called with the result of the decorated function and any
    extras

* ``instead`` - run a callable in place of the decorated function

  * by default called with the args and kwargs to the decorated function,
    along with a reference to the function itself

* ``decorate`` - specify multiple callables to be run before, after, and/or
  instead of the decorated function

  * callables passed to ``decorate``'s ``before``, ``after``, or ``instead``
    keyword arguments will be called with the same default function signature
    as described for the individual decorators, above. Extras will be
    passed to all provided callables

Every generic decorator takes any number of keyword arguments, which will be
passed directly into the provided callable, unless ``unpack_extras`` is False
(see below), so, running the code below prints "red":

.. code:: python

    from pydecor import before

    def before_func(label=None):
        print(label)

    @before(before_func, label='red')
    def red_function():
        pass

    red_function()

Every generic decorator takes the following keyword arguments:

* ``pass_params`` - if True, passes the args and kwargs, as a tuple and
  a dict, respectively, from the decorated function to the provided callable
* ``pass_decorated`` - if True, passes a reference to the decorated function
  to the provided callable
* ``implicit_method_decoration`` - if True, decorating a class implies
  decorating all of its methods. **Caution:** you should probably leave this
  on unless you know what you are doing.
* ``instance_methods_only`` - if True, only instance methods (not class or
  static methods) will be automatically decorated when
  ``implicit_method_decoration`` is True
* ``unpack_extras`` - if True, extras are unpacked into the provided callable.
  If False, extras are placed into a dictionary on ``extras_key``, which
  is passed into the provided callable.
* ``extras_key`` - the keyword to use when passing extras into the provided
  callable if ``unpack_extras`` is False

Convenience
~~~~~~~~~~~

* ``intercept`` - catch the specified exception and optionally re-raise and/or
  call a provided callback to handle the exception
* ``log_call`` - automatically log the decorated function's call signature and
  results

**More to come!!** See Roadmap_ for more details on upcoming features

Stacking
********

Generic and convenience decorators may be stacked! You can stack multiple
of the same decorator, or you can mix and match. Some gotchas are listed
below.

Generally, staciking works just as you might expect, but some care must be
taken when using the ``@instead`` decorator, or ``@intercept``, which
uses ``@instead`` under the hood.

Just remember that ``@instead`` replaces everything that comes before. So,
if long as ``@instead`` calls the decorated function, it's okay to stack it.
In these cases, it will be called *before* any decorators specified below
it, and those decorators will be executed when it calls the decorated function.
``@intercept`` behaves this way.

If an ``@instead`` decorator does *not* call the decorated function and
instead replaces it entirely, it **must** be specified first (at the bottom
of the stacked decorator pile), otherwise the decorators below it will not
execute.

For ``@before`` and ``@after``, it doesn't matter in what order the decorators
are specified. ``@before`` is always called first, and then ``@after``.


Class Decoration
****************

Class decoration is difficult, but PyDecor aims to make it as easy and
intuitive as possible!

By default, decorating a class applies that decorator to all of that class'
methods (instance, class, and static). The decoration applies to class and
static methods whether they are referenced via an instance or via a class
reference. "Extras" specified at the class level persist across calls to
different methods, allowing for things like a class level memoization
dictionary (there's a very basic test in the test suite
that demonstrates this pattern, and a convenient memoization decorator
is scheduled for the next release!).

If you'd prefer that the decorator not apply to class and static methods,
set the ``instance_methods_only=True`` when decorating the class.

If you want to decorate the class itself, and *not* its methods, keep in
mind that the decorator will be triggered when the class is instantiated,
and that, if the decorator replaces or alters the return, that return will
replace the instantiated class. With those caveats in mind, setting
``implicit_method_decoration=False`` when decorating a class enables that
funcitonality.

.. note::

    Class decoration, and in particular the decoration of class and static
    methods, is accomplished through some pretty deep, complicated magic.
    The test suite has a lot of tests trying to make sure that everything
    works as expected, but please report any bugs you find so that I
    can resolve them!


Method Decoration
*****************

Decorators can be applied to static, class, or instance methods directly, as
well. If combined with ``@staticmethod`` or ``@classmethod`` decorators,
those decorators should always be at the "top" of the decorator stack
(furthest from the function).

When decorating instance methods, ``self`` is removed from the parameters
passed to the provided callable.

When decorating class methods, ``cls`` is removed from the parameters passed
to the provided callable.

Currently, the class and instance references *do not* have to be named
``"cls"`` and ``"self"``, respectively, in order to be removed. However,
this is not guaranteed for future releases, so try to keep your naming
standard if you can (just FYI, ``"self"`` is the more likely of the two to
wind up being required).

Examples
********

Below are some examples for the generic and standard decorators. Please
check out the API Docs for more information, and also check out the
convenience decorators, which are all implemented using the
``before``, ``after``, and ``instead`` decorators from this library.

Update a Function's Args or Kwargs
----------------------------------

Functions passed to ``@before`` can either return None, in which case nothing
happens to the decorated functions parameters, or they can return a tuple
of args (as a tuple) and kwargs (as a dict), in which case those parameters
are used in the decorated function. In this example, we sillify a very
serious function.

.. note::
    Because kwargs are mutable, they can be updated even if the function
    passed to before doesn't return anything.

.. code:: python

    from pydecor import before

    def spamify_func(args, kwargs):
        """Mess with the function arguments"""
        args = tuple(['spam' for _ in args])
        kwargs = {k: 'spam' for k in kwargs}
        return args, kwargs


    @before(spamify_func, pass_params=True)
    def serious_function(serious_string, serious_kwarg='serious'):
        """A very serious function"""
        print('A serious arg: {}'.format(serious_string))
        print('A serious kwarg: {}'.format(serious_kwarg))

    serious_function('Politics', serious_kwarg='Religion')

The output?

.. code::

    A serious arg: spam
    A serious kwarg: spam

Do Something with a Function's Return Value
-------------------------------------------

Functions passed to ``@after`` receive the decorated function's return value
by default. If ``@after`` returns None, the return value is sent back
unchanged. However, if ``@after`` returns something, its return value is
sent back as the return value of the function.

In this example, we ensure that a function's return value has been thoroughly
spammified.

.. code:: python

    from pydecor import after

    def spamify_return(result):
        """Spamify the result of a function"""
        return 'spam-spam-spam-spam-{}-spam-spam-spam-spam'.format(result)


    @after(spamify_return)
    def unspammed_function():
        """Return a non-spammy value"""
        return 'beef'

    print(unspammed_function())

The output?

.. code::

    spam-spam-spam-spam-beef-spam-spam-spam-spam


Do Something Instead of a Function
----------------------------------

Functions passed to ``@instead`` by default receive the args and kwargs of
the decorated function, along with a reference to that function. But, they
don't *have* to receive anything. Maybe you want to skip a function when
a certain condition is True, but you don't want to use ``pytest.skipif``,
because ``pytest`` can't be a dependency of your production code for
whatever reason.


.. code:: python

    from pydecor import instead

    def skip(args, kwargs, decorated, when=False):
        if when:
            pass
        else:
            return decorated(*args, **kwargs)


    @instead(skip, when=True)
    def uncalled_function():
        print("You won't see me (you won't see me)")


    uncalled_function()

The output?

(There is no output, because the function was skipped)


Roadmap
-------

1.1.0
*****

More Convenience Decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following convenience decorators will be included in the ``1.1.0``
release:

* ``export`` - add the decorated item to ``__all__``
* ``skipif`` - similar to py.test's decorator, skip the function if a
  provided condition is True
* ``memoize`` - store function results in a local dictionary cache

Let me know if you've got any idea for other decorators that would
be nice to have!

Typing Stubfiles
~~~~~~~~~~~~~~~~

Right now type hints are provided via rst-style docstring specification.
Although this format is supported by PyCharm, it does not conform to the
type-hinting standard defined in `PEP 484`_.

In order to better conform with the new standard (and to remain compatible
with Python 2.7), stubfiles will be added for the ``1.1.0`` release,
and docstring hints will be removed so that contributors don't have
to adjust type specifications in two places.



Credits and Links
-----------------

* This project was started using my generic `project template`_
* Tests are run with pytest_ and tox_
* Mocking in Python 2.7 tests uses the `mock backport`_
* Python 2/3 compatible exception raising via six_
* The `typing backport`_ is used for Python2.7-3.4-compatible type definitions
* Documentation built with sphinx_
* Coverage information collected with coverage_

.. _`project template`: https://github.com/mplanchard/python_skeleton
.. _pytest:
.. _`py.test`: https://docs.pytest.org/en/latest/
.. _tox: http://tox.readthedocs.org/
.. _sphinx: http://www.sphinx-doc.org/en/stable/
.. _coverage: https://coverage.readthedocs.io/en/coverage-4.4.1/
.. _`mock backport`: https://mock.readthedocs.io/en/latest/#
.. _`pep 484`: https://www.python.org/dev/peps/pep-0484/
.. _six: https://pythonhosted.org/six/
.. _`typing backport`: https://pypi.org/project/typing/
