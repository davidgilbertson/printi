Printi
==========

Printi watches ``stdout`` and if it sees a number
that can be displayed in a more interesting way, it
will tell you. E.g. the last line below is from ``printi``

.. code-block:: python

  >>> import math
  >>> import printi
  >>> printi.watch()
  >>> math.sin(math.pi / 4)
  0.7071067811865476
  💡 0.7071067811865476 ≈ 1/√2

API
==========

``printi.watch()``
------------------

Will start watching. You can add this to your startup script

``printi.unwatch()``
------------------

Will stop watching.

``printi(printargs)``
------------------

``printi`` is also a replacement for ``print``. If you'd rather not use
``printi.watch()``, you can instead use ``printi`` directly. It has the same
API as ``print``

``printi.update_config()``
--------------------------
Updates the config.

TODO (@davidgilbertson): more info.

Development
===========

  * Run ``pipenv run test`` to run the tests
  * Run ``py -m build`` to build
