|Travis|_ |PyPi|_

.. |Travis| image:: https://api.travis-ci.org/kmaehashi/pypict.svg?branch=master
.. _Travis: https://travis-ci.org/kmaehashi/pypict

.. |PyPi| image:: https://badge.fury.io/py/pypict.svg
.. _PyPi: https://badge.fury.io/py/pypict


PyPICT
======

Python binding library for `Microsoft PICT <https://github.com/Microsoft/pict>`__ (Pairwise Independent Combinatorial Tool).

Installation
------------

::

    $ git clone https://github.com/kmaehashi/pypict.git
    $ cd pypict
    $ git submodule init
    $ git submodule update
    $ python setup.py build_pict
    $ pip install -U .

APIs
----

There are four different APIs provided in this library.

* Low-level API (``pypict.capi``) provides Python functions that map to each `PICT C API function <https://github.com/Microsoft/pict/blob/master/api/pictapi.h>`__.
* High-level API (``pypict.api``) wraps the low-level API to provide automatic memory management.
* Tools API (``pypict.tools``) wraps the high-level API to provide convenient features.
* Command API (``pypict.cmd``) is a thin wrapper for ``pict`` command.
  Note that this API does not use features from PICT C API shared library.
