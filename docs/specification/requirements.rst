Requirements
=============

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

.. req:: Low memory utilisation
   :id: CODEC_REQ_5
   :status: open

   The encoder must use <2K of RAM and <16K of non-volatile FRAM, as can be found on an
   MSP430FR2033 microcontroller.

.. req:: No configuration from the user
   :id: CODEC_REQ_7
   :status: complete

   The encoder must not require any set up or configuration from the user.

.. req:: Minimal power consumption.
   :id: CODEC_REQ_9
   :status: complete

   The encoder is designed to run on hardware that can run for years on a CR1620 battery.

.. req:: Minimise EEPROM wear.
   :id: CODEC_REQ_8
   :status: complete

   The encoder must not write to the same EEPROM block too frequently. Each has a write endurance of
   roughly 100,000 cycles.

.. req:: Self containment
   :id: CODEC_REQ_10
   :status: complete

   The URL must contain all information needed by the decoder. There will be no need to
   store and retrieve data from an external source (database).

   By consequence one decoder instance can be substituted for another.

.. req:: Status information
   :id: CODEC_REQ_11
   :status: complete

   The URL must convey status information. This is used by the decoder and an end-user
   to determine if the encoder and the microcontroller it is running on are ok.

   Status information changes infrequently compared to environmental sensor data.


Decoder
--------

.. req:: Decoder parses URL parameters
   :id: CODEC_REQ_2
   :status: open

   The decoder performs the reverse operation of the encoder. It takes parameters from the URL
   and returns environmental sensor data and metadata from them.



