Encoder
========

Initialise
-----------

Start with a call to :cpp:func:`sample_init()`. This creates an NDEF message with one URI record. The latter
consists of the :ref:`baseurl` followed by a query string.

The query string has several parameters, such as :ref:`time-interval`, :ref:`version` and a serial.

Append Samples
---------------

Update minutes elapsed in the end stop
---------------------------------------

Non-volatile Parameters
-------------------------

These include the :ref:`serial`, secret key, time interval and base url fields.
They are stored in the user memory section of the MSP430.
