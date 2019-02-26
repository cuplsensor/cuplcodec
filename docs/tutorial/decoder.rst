Decoder
========

Decode a URL
--------------
Use the :class:`urldecoder.urldecoder.UrlDecoder` class



Create and install the Python Package
--------------------------------------

A Python package is created so that the urldecoder can
be used easily by other applications such as PSWebApp.

This is based on the instructions at
https://packaging.python.org/tutorials/packaging-projects/


1. In the command line navigate to PSCodec/urldecoder
2. Increase the version number in setup.py
3. Generate the tar.gz source archive and .whl built distribution::

    python3 setup.py sdist bdist_wheel

4. Install the urldecoder module::

    pipenv install --find-links=./dist urldecoder