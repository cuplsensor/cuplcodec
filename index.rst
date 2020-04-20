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

.. req:: Encoder writes a message
   :id: CODEC_REQ_1
   :status: open

   The encoder takes environmental sensor data and writes it into a message
   that can be opened and read automatically by most mobile phones.

.. spec:: NDEF message
   :id: CODEC_SPEC_1
   :links: CODEC_REQ_1

   The message format is NDEF. This is used to transmit data to a phone using NFC.

   Outgoing links of this spec: :need_outgoing:`CODEC_SPEC_1`.

.. feature::
   :id: CODEC_FEATURE_1
   :links: CODEC_SPEC_1

   The NDEF message has one URL record.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
