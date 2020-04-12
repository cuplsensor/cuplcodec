Encoder
========

Initialise
-----------

Start with a call to :cpp:func:`sample_init`. This creates an NDEF message with one URI record.
The latter consists of the :ref:`base-url` followed by a query string.

The query includes parameters :ref:`time-interval`, :ref:`version` and :ref:`serial`. These data do not
change subsequent to initialisation.

The final parameter in the query string is 'q='. Its value is the circular buffer of sensor data.
This is a few hundred characters long. The character after 'q=' must fall on an EEPROM block boundary.

The circular buffer grows to a maximum length of (:cpp:`buflensamples`) as samples are added.
Regardless, it is always encoded into a base64 string of fixed length. This is due to a constraint:
the NDEF message has a fixed length defined by :ref:`payload-length`. This is not altered after initialisation.
The constraint is imposed to simplify code, reduce power consumption and minimise wear on EEPROM block 0.

To this end, the circular buffer parameter is initialised with a repeating sequence 'MDaW' for its
entire length. Each 4-byte MDaW decodes to 3-bytes all zeros.


Append Samples
---------------

Update minutes elapsed in the end stop
---------------------------------------

Non-volatile Parameters
-------------------------

These include the :ref:`serial`, secret key, :ref:`time-interval` and :ref:`base-url` fields.
They are stored in the user memory section of the MSP430.
