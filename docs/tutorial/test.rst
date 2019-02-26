Test
=====

Overview
------------
The encoder is written in C. The C Foreign Function Interface (CFFI) compiles
selected encoder modules and their dependencies into a Python
shared object (see :meth:`pyencoder.unitc.load`).

The shared object is imported into another Python script, which makes
calls to the C functions inside.

CFFI can replace C function definitions with Python.
This is required for functions that normally depend on hardware,
such as :cpp:func:`nt3h_writetag()` and :cpp:func:`nt3h_readtag()`.
Objects derived from :class:`pyencoder.instrumented.InstrumentedBase`
redirect the two functions above to write to and read from a mock EEPROM,
written in Python.

The mock EEPROM is a bytearray that can be accessed in 16-byte blocks. Its
contents can be read out raw or parsed as an NDEF message using the NDEF library.

Example 2
----------
Call :cpp:func:`ndef_writeblankurl()` to write a
URL within a URI record inside an NDEF message to EEPROM.

To return the URL from the mock EEPROM as a string use.
:meth:`pyencoder.eeprom.get_url`

Example
--------
The following example covers how to build pyencoder and run unit tests on the
NDEF encoder module.

First run::

  pipenv run python pyencoder/builder.py

This will cause CFFI to compile the C modules into shared objects
for your platform. The *.so files are written to the pyencoder/sharedobjects directory.

To perform unit tests on the NDEF module run::

  pipenv run pytest ndeftests.py

Low level tests
----------------

High level tests
-----------------
