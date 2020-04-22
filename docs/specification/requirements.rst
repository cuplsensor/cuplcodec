Requirements
=============

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

.. req:: Encoder message is written blockwise to EEPROM
   :id: CODEC_REQ_9

   The encoder does not output a 1000 character string. 1K of RAM is a lot for a
   microcontroller. Instead it is designed to output an I2C EEPROM, which is arranged into
   16-byte blocks. A maximum of 4 EEPROM blocks are written to or read from at a time.

.. req:: Decoder parses URL parameters
   :id: CODEC_REQ_2
   :status: open
   :links: CODEC_REQ_3

   The decoder performs the reverse operation of the encoder. It takes parameters from the URL
   and returns environmental sensor data and metadata from them.

.. req:: Encoder must run on a low cost MSP430.
   :id: CODEC_REQ_5
   :status: open

   The encoder must run with minimal resources and without an RTOS.

.. req:: No configuration from the user
   :id: CODEC_REQ_80
   :status: complete

   The encoder must not require any set up or configuration from the user.

.. req:: Minimal power consumption.
   :id: CODEC_REQ_9
   :status: complete

   The encoder is designed to run on hardware that should run for years on a
   small coin cell battery.

.. req:: Minimise EEPROM wear.
   :id: CODEC_REQ_8
   :status: complete

   The encoder must not write to the same EEPROM block too frequently. Each has a write endurance of
   roughly 100,000 cycles.

.. req:: Database lookups not required.
   :id: CODEC_REQ_10
   :status: complete

   Encoded URL must contain all information needed by the decoder. There must be no need to
   perform a database lookup. By consequence one decoder instance can be substituted for another.

