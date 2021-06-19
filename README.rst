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

* Microsoft PICT 3.7.1
* Python 3.6 / 3.7 / 3.8 / 3.9

Installation
------------

Wheels (binary distribution) are available for Linux (x86_64).
The PICT shared library is included in wheels.

::

    $ pip install pypict

On other platforms, you need to build from source.
PICT source tree is registered as a submodule of this repository.
``python setup.py build_pict`` will run ``make`` command to build PICT shared library inside the tree.
You need to manually install the shared library and command, or set path of the tree to the appropriate environment variables (``PATH``, ``LD_LIBRARY_PATH``, etc.)

::

    $ git clone --recursive https://github.com/kmaehashi/pypict.git pypict
    $ cd pypict
    $ python setup.py build_pict
    $ pip install -U .
    $ export PATH=${PWD}/pict:${PATH}
    $ export LD_LIBRARY_PATH=${PWD}/pict:${LD_LIBRARY_PATH}

APIs
----

There are different layers of API provided in this library.

Low-level API (``pypict.capi``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Low-level API provides Python functions that map to each `PICT C API function <https://github.com/Microsoft/pict/blob/main/api/pictapi.h>`__.

.. code-block:: python

    >>> import pypict.capi
    >>> task = pypict.capi.createTask()
    >>> print(task)
    14042112
    >>> pypict.capi.deleteTask(task)

CLIDLL API (``pypict.capi.execute``), which accepts a PICT command line arguments and returns the output, is also available.

.. code-block:: python

    >>> import pypict.capi
    >>> output = pypict.capi.execute(['example/example.model', '/o:2'])
    >>> print(output)
    Type    Size    Format method   File system     Cluster size    Compression
    Mirror  100     Quick           FAT             2048            Off
    ...

Note that CLIDLL API directly writes to the stderr when warnings are generated.

You can use ``pypict`` module as a command that behaves like PICT command line tool (e.g., ``python -m pypict example/example.model /o:2``).

High-level API (``pypict.api``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

High-level API wraps the low-level API to provide automatic memory management with RAII API.

.. code-block:: python

    >>> import pypict.api
    >>> task = pypict.api.Task()
    >>> task.model.add_parameter(2)
    19976288
    >>> task.model.add_parameter(3)
    20013488
    >>> list(task.generate())
    [[1, 0], [0, 1], [1, 1], [0, 2], [1, 2], [0, 0]]

Command API (``pypict.cmd``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command API wraps the CLIDLL API.

.. code-block:: python

    >>> import pypict.cmd
    >>> pypict.cmd.from_model('''
    ... X: 1, 2
    ... Y: 3, 4
    ... ''')
    (['X', 'Y'], [['2', '4'], ['2', '3'], ['1', '4'], ['1', '3']])
