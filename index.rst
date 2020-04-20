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
   that can be opened and read automatically by most mobile phones.

.. spec:: Message format
   :id: CODEC_SPEC_1
   :links: CODEC_REQ_1

   The message format is NDEF. This is used to transmit data to a phone using NFC.

   Outgoing links of this spec: :need_outgoing:`CODEC_SPEC_1`.

.. feat::
   :id: CODEC_FEATURE_1
   :links: CODEC_SPEC_1
   :status: open

   The NDEF message has one URL record.

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

.. spec:: Customisable NDEF fields
   :id: CODEC_SPEC_2
   :status: open
   :links: CODEC_REQ_4

   The NDEF message can be customised in several ways.

.. feat:: Base URL can be modified.
   :id: CODEC_FEATURE_2
   :links: CODEC_SPEC_2

   The base URL can be changed. It is recommended to keep this as short as possible to
   allow more room for environmental sensor data.





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
