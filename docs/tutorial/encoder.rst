Encoder
========

Initialise
-----------

Start with a call to :cpp:func:`sample_init(unsigned int, bool)`. This creates an NDEF message with one URI record.
The latter consists of the :ref:`baseurl` followed by a query string.

This includes the parameters :ref:`time-interval`, :ref:`version` and :ref:`serial`. These data will not
change subsequently.

Append Samples
---------------

Update minutes elapsed in the end stop
---------------------------------------

Non-volatile Parameters
-------------------------

These include the :ref:`serial`, secret key, :ref:`time-interval` and :ref:`baseurl` fields.
They are stored in the user memory section of the MSP430.
