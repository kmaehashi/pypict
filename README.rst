|Travis|_ |PyPi|_

.. |Travis| image:: https://api.travis-ci.com/kmaehashi/pypict.svg?branch=master
.. _Travis: https://travis-ci.org/kmaehashi/pypict

.. |PyPi| image:: https://badge.fury.io/py/pypict.svg
.. _PyPi: https://badge.fury.io/py/pypict


PyPICT
======

Python binding library for `Microsoft PICT <https://github.com/Microsoft/pict>`__ (Pairwise Independent Combinatorial Tool).

Requirements
------------

* Microsoft PICT
* Python 2.7, 3.4, 3.5 or 3.6

Installation
------------

Wheels (binary distribution) are available for Linux.
PICT shared library and command is included in wheels.

::

    $ pip install pypict

On other platforms, you need to build from source.
PICT source tree is registered as submodule of this repository.
``python setup.py build_pict`` will run ``make`` command to build PICT shared library inside the tree.
You need to manually install the shared library and command, or set path of the tree to the appropriate environment variables (``PATH``, ``LD_LIBRARY_PATH``, etc.)

::

    $ git clone https://github.com/kmaehashi/pypict.git
    $ cd pypict
    $ git submodule init
    $ git submodule update
    $ python setup.py build_pict
    $ pip install -U .
    $ export PATH=${PWD}/pict:${PATH}
    $ export LD_LIBRARY_PATH=${PWD}/pict:${LD_LIBRARY_PATH}

APIs
----

There are four different APIs provided in this library.
Generally you only need to use Tools API (``pypict.tools``).

* Low-level API (``pypict.capi``) provides Python functions that map to each `PICT C API function <https://github.com/Microsoft/pict/blob/master/api/pictapi.h>`__.
* High-level API (``pypict.api``) wraps the low-level API to provide automatic memory management.
* Tools API (``pypict.tools``) wraps the high-level API to provide convenient features.
* Command API (``pypict.cmd``) is a thin wrapper for ``pict`` command.
  This API uses PICT command directly instead of PICT shared library.

Example
-------

Here is an example usage of Tools API to generate pair-wise patterns from parameter set.

.. code-block:: python

    import pypict.tools

    params = {
        "Type":          ["Single", "Span", "Stripe", "Mirror", "RAID-5"],
        "Size":          ["10", "100", "500", "1000", "5000", "10000", "40000"],
        "Format method": ["Quick", "Slow"],
        "File system":   ["FAT", "FAT32", "NTFS"],
        "Cluster size":  ["512", "1024", "2048", "4096", "8192", "16384", "32768", "65536"],
        "Compression":   ["On", "Off"],
    }

    for case in pypict.tools.from_dict(params):
        print(case)
