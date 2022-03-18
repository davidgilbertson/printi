🚧 This Python package is a WIP.

Still TODO:

☐ Publish to PyPi/conda-forge

☐ Make it work for older versions than 3.10

☐ Test with macOS/Linux

☐ Test with Jupyter

Printi
======

Printi watches what you print, and if it sees a number
that can be displayed in a more insightful way, it
will tell you.

For example, the last line in the code snippet below is ``printi`` telling you
that ``-2.4674011002723395`` is very very close to ``-π²/4``:

.. code-block:: python

  >>> import cmath
  >>> import printi
  >>> printi.watch()
  >>> cmath.log(1j) ** 2
  (-2.4674011002723395+0j)
  💡 -2.4674011002723395 ≈ -π²/4

API
===

``printi()``
---------------------

The ``printi`` function is a drop-in replacement for ``print``. It has the same
API as the builtin ``print`` function.

To use ``printi`` as a function, you'll need to use ``from printi import printi`` (for all
other methods it is enough to use ``import printi``).

``printi.watch()``
------------------

Rather than use ``printi()`` directly, you can tell it to watch ``stdout``.
You can add this to your startup script
referenced by `PYTHONSTARTUP <https://docs.python.org/3/using/cmdline.html#envvar-PYTHONSTARTUP>`_.

Example Python startup file using Printi:

.. code-block:: Python

  # This file is referenced in PYTHONSTARTUP
  import sys
  from pathlib import Path

  sys.path.append(str(Path.home() / 'path/to/printi/src'))
  from printi import printi

  printi.watch()

Now when you start any interactive session, Printi will be watching.

``printi.unwatch()``
--------------------

Printi will stop watching.

``printi.update_config()``
--------------------------
Updates the configuration options for Printi. All possible keys, and their defaults are:

.. code-block:: python

  printi.update_config(
    min_denominator=3,
    max_denominator=100,
    tol=1e-9,
    symbol='💡',
    specials={
        math.pi: 'π',
        math.tau: 'τ',
        math.e: 'e',
    },
  )

* ``min_denominator`` is the minimum denominator.
* ``max_denominator`` is the max. If this is set too high, you'll get false positives
* ``tol`` is the tolerance. This is passed to ``math.isclose`` as ``rel_tol``
* ``symbol``. Change this if you don't like the light bulb. Why don't you like the light bulb?
* ``specials`` is a dict of ``float``/``string`` pairs that will be added to the existing dict.
  To remove a key, pass ``None`` as the value. Example below:

  .. code-block:: python

    >>> printi.update_config(specials={1.2345678: 'λ'})
    >>> 'How do you like 1.2345678?'
    'How do you like 1.2345678?'
    💡 1.2345678 ≈ λ

Limitations
===========

Printi will only find 'representations' in the form a ± b * c ** d where

* ``a`` is an integer
* ``b`` is a fraction (respecting min/max denominator)
* ``c`` is either one of the 'special' values, or a digit
* ``d`` is a selection of positive and negative integers and fractions

Check out the tests in ``/tests/test_printi.py`` for lots of examples.

Development
===========

* Run ``pipenv run test`` to run the tests
* Run ``py -m build`` to build
