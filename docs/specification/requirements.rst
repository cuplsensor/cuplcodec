Requirements
=============

.. needflow:: My first needflow
   :scale: 30
   :filter: ("bit" not in tags) and (type != "impl")

.. req:: Codec comprises an encoder and decoder.
   :id: CODEC_REQ_3
   :status: open

   The codec comprises has two parts:

   1. An encoder that produces an URL from raw data.
   2. A decoder that recovers raw data from the URL.

Encoder
--------

.. req:: Encoder writes a message
   :id: CODEC_REQ_1
   :status: open
   :links: CODEC_REQ_3

   The encoder takes environmental sensor data and writes it into a message
   that is opened and read automatically by most mobile phones.

.. req:: Encoder shall run on a low cost, low power microcontroller
   :id: CODEC_REQ_12
   :status: open

   The encoder will run on an inexpensive microcontroller. This will be powered
   by a coin cell battery and should run for years.

.. req:: No configuration from the user
   :id: CODEC_REQ_7
   :status: complete

   The encoder must not require any set up or configuration from the user.

.. req:: Message is written to EEPROM
   :id: CODEC_REQ_8
   :status: complete
   :links: CODEC_REQ_1

   The encoder must not write to the same EEPROM block too frequently. Each has a write endurance of
   roughly 100,000 cycles.

   Status information changes infrequently compared to environmental sensor data.

Decoder
--------

.. req:: Decoder reproduces encoder data
   :id: CODEC_REQ_2
   :status: open
   :links: CODEC_REQ_3

   The decoder must reproduce data fed into the encoder.



