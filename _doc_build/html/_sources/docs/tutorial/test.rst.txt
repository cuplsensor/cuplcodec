Install
========

Create the Python Package Distributions
-----------------------------------------

A Python package is created so that the urldecoder can
be used easily by other applications such as PSWebApp.

This is based on the instructions at
https://packaging.python.org/tutorials/packaging-projects/

1. In the command line navigate to PSCodec/urldecoder
2. Increase the version number in setup.py
3. Generate the tar.gz source archive and .whl built distribution::

    python3 setup.py sdist bdist_wheel

Generating bdist_wheel will invoke GCC, to call the compile() method on the ffibuilder objects defined in build scripts
such as ndef_builder.py The result is a sharedobject binary for each script, which can later be imported.
All build scripts and links to the ffibuilder objects within are inside the cffi_modules field of setup.py

I used Building_Chuck_Norris_Part_5_ and Building_and_distributing_packages_with_setuptools_
and Preparing_and_distributing_cffi_modules_ as guidance.

Installing from source requires the GCC compiler. If the person installing is using a platform compatible with a wheel,
(same OS, same Python version and compatible C libraries) then they can used the precompiled binaries inside that.

.. _Building_Chuck_Norris_Part_5: https://dmerej.info/blog/post/chuck-norris-part-5-python-cffi/
.. _Building_and_distributing_packages_with_setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html
.. _Preparing_and_distributing_cffi_modules: https://cffi.readthedocs.io/en/latest/cdef.html

Install the Python package in a pipenv
----------------------------------------

Install the pscodec module from a source file::

    pipenv install dist/PSCodec-0.0.4.tar.gz

Install the pscodec from a wheel::

    pipenv install dist/PSCodec-0.0.4-cp36-cp36m-macosx_10_13_x86_64.whl

Develop C and run tests from the latest source code
-----------------------------------------------------

This installs the package in place and compiles any sharedobject modules for c_encoder::

    python setup.py develop



Build Documentation
--------------------

Edit restructuredtext files inside the docs folder. Then run::

    python run make html



Test
-----

To run tests invoke pytest::

    pipenv run pytest encoder/test_ndef.py

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

