Encoder
========

Initialise
-----------

Start with a call to :cpp:func:`sample_init`. This creates an NDEF message with one URI record.
The latter consists of the :ref:`base-url` followed by a query string.

The query includes parameters :ref:`time-interval`, :ref:`version` and :ref:`serial`. These data do not
change subsequent to initialisation.

The final parameter in the query string is 'q='. Its value is the circular buffer, which holds sensor data.
This is a few hundred characters long. For simplicity, the character after 'q=' must fall on an EEPROM block boundary.
The circular buffer is initialised to 'all zeros'. After base64 encoding this will appear as a repeating
sequence 'MDaW'. 

Append Samples
---------------

Update minutes elapsed in the end stop
---------------------------------------

Non-volatile Parameters
-------------------------

These include the :ref:`serial`, secret key, :ref:`time-interval` and :ref:`base-url` fields.
They are stored in the user memory section of the MSP430.
