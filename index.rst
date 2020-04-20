Plotsensor Codec Documentation
===================================

.. _index:
.. toctree::
   :maxdepth: 2

   docs/tutorial/index
   docs/tutorial/encoder
   docs/tutorial/decoder
   docs/tutorial/test
   docs/reference/urldecoder
   docs/reference/encoder
   docs/reference/pyencoder

   :caption: Contents:

How to build this documentation
--------------------------------
.. req:: Codec comprises an encoder and decoder.
   :id: CODEC_REQ_3
   :status: open

   The codec is two pieces of software: an encoder and a decoder.
   One performs the reverse operation of the other.

.. req:: Encoder writes a message
   :id: CODEC_REQ_1
   :status: open
   :links: CODEC_REQ_3

   The encoder takes environmental sensor data and writes it into a message
   that is opened and read automatically by most mobile phones.

.. spec:: Message format
   :id: CODEC_SPEC_1
   :links: CODEC_REQ_1

   The message format is NDEF. This is used to transmit data to a phone using NFC.
   An NDEF message has 3 fields: Type, Length and Value.

   +-----------+------------------------+----------------------+----------------------+
   | NDEF Msg. | :need:`CODEC_FEAT_1`   | :need:`CODEC_FEAT_3` | Value                |
   +-----------+------------------------+------+-----+---------+----------------------+
   | Byte      | 0                      | 1    | 2   | 3       | 4...                 |
   +-----------+------------------------+------+-----+---------+----------------------+
   | Data      | 0x03                   | 0xFF | MSB | LSB     | :need:`CODEC_SPEC_3` |
   +-----------+------------------------+------+-----+---------+----------------------+

.. feat:: NDEF message type
   :id: CODEC_FEAT_1
   :links: CODEC_SPEC_1

   The message type is 0x03, corresponding to a known type.

.. feat:: NDEF message length
   :id: CODEC_FEAT_3
   :links: CODEC_SPEC_1

   The message length is 3 bytes. It cannot change after the message has been created.

.. spec:: NDEF URL record
   :id: CODEC_SPEC_3
   :links: CODEC_SPEC_1
   :status: open

   Sensor data are stored in a URL record. As it is the only one in the message and of a known type,
   a phone opens the URL automatically in its default web browser.

+-----------+------+------------------+-----------------------------------------------------------------------------+
| NDEF Msg. | Type | Length           | Value                                                                       |
+-----------+------+------------------+----------------------------------------------------------------+------------+
| NDEF Rec. |                         | Header                                                         | Payload    |
+-----------+------+------+-----+-----+--------+----------+---------------+----------------+-----------+------------+
|           |      |      |     |     | Rec Hdr| Type Len | `Payload Length`_              | Rec. Type | URL Prefix |
+-----------+------+------+-----+-----+--------+----------+-------+-------+-------+--------+-----------+------------+
| Byte      | 0    | 1    | 2   | 3   | 4      | 5        | 6     | 7     | 8     | 9      | 10        | 11         |
+-----------+------+------+-----+-----+--------+----------+-------+-------+-------+--------+-----------+------------+
| Data      | 0x03 | 0xFF | MSB | LSB |        | 0x01     | PL[3] | PL[2] | PL[1] | PL[0]  | 0x55      | 0x03       |
+-----------+------+------+-----+-----+--------+----------+---+---+---+---+-------+--------+-----------+------------+


.. req:: Decoder parses URL parameters
   :id: CODEC_REQ_2
   :status: open
   :links: CODEC_REQ_3

   The decoder performs the reverse operation of the encoder. It takes parameters from the URL
   and returns environmental sensor data and metadata from them.

.. req:: The NDEF message is customisable.
   :id: CODEC_REQ_4
   :status: open
   :links: CODEC_REQ_1

.. spec:: Customisable NDEF properties
   :id: CODEC_SPEC_2
   :status: open
   :links: CODEC_REQ_4

   The NDEF message can be customised in several ways.

.. feat:: Base URL can be modified.
   :id: CODEC_FEATURE_2
   :links: CODEC_SPEC_2

   The base URL can be changed. It is recommended to keep this as short as possible to
   allow more room for environmental sensor data.

.. req:: Encoder must run on a low cost MSP430.
   :id: CODEC_REQ_5
   :status: open

   The encoder must run with minimal resources and without an RTOS.

.. spec:: Features for low resource use.
   :id: CODEC_SPEC_4
   :status: open
   :links: CODEC_REQ_5

.. feat:: Only static memory allocation is used.
   :id: CODEC_FEAT_4
   :status: open
   :links: CODEC_SPEC_4

   The stdio library needed for malloc takes a lot of available memory on the MSP430, so it is not used.
   The size of the circular buffer is fixed at compile time (move).

.. feat:: Encoder is written in C.
   :id: CODEC_FEAT_6
   :status: open
   :links: CODEC_SPEC_4

   There is little benefit to C++ given the low complexity of the encoder.

.. req:: Encoder does not require an absolute timestamp
   :id: CODEC_REQ_7
   :status: complete
   :links: CODEC_REQ_1

   The base URL output from the encoder does not feature an absolute timestamp. 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
