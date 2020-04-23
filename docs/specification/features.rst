Features
=========

NDEF message
--------------

.. feat:: NDEF message type
   :id: CODEC_FEAT_1
   :links: CODEC_SPEC_1

   The message type is 0x03, corresponding to a known type.

.. feat:: NDEF message length
   :id: CODEC_FEAT_2
   :links: CODEC_SPEC_1

   The message length is 3 bytes. It cannot change after the message has been created.

NDEF record
--------------

.. feat:: Payload length
   :id: CODEC_FEAT_3
   :status: open
   :links: CODEC_SPEC_3

   Length of the NDEF record payload length in bytes. Similar to :need:`CODEC_FEAT_2`,
   it cannot change after the record has been created.

.. feat:: Type length
   :id: CODEC_FEAT_4
   :status: open
   :links: CODEC_SPEC_3

   Length of the :need:`CODEC_FEAT_5` field in bytes. This is 1 byte.

.. feat:: Record type
   :id: CODEC_FEAT_5
   :status: open
   :links: CODEC_SPEC_3

   NDEF record type is 0x55, which corresponds to a URI record.

Other
------

.. feat:: Samples are timestamped without an absolute timestamp
   :id: CODEC_FEAT_6
   :links: CODEC_SPEC_10, CODEC_SPEC_6

   The base URL output from the encoder cannot include an absolute timestamp. This would
   need to be set by the user after powering on the microcontroller that runs the encoder.

   All samples are timestamped relative to the time that the decoder is run. It
   is assumed that the time difference between when the encoded message is read (by a phone) and
   the time the decoder is run (on a web server) is much less than one minute.

   The timestamping algorithm is as follows:
   #. Samples are put in order of recency.
   #. Minutes elapsed since the most recent sample is extracted from the URL.
   #. Current time (now in UTC) is determined.
   #. The first sample is assigned a timestamp = now - minutes elapsed.
   #. Minutes between samples is extracted from the URL. This is used to timestamp each sample
   relative to the first.

.. feat:: Base URL can be modified.
   :id: CODEC_FEAT_7

   The base URL can be changed. It is recommended to keep this as short as possible to
   allow more room for environmental sensor data.

Low resource utilisation
-----------------------
.. feat:: Encoder writes to EEPROM blocks.
   :id: CODEC_FEAT_13
   :status: open
   :links: CODEC_SPEC_4

   The encoder cannot output the 1000 character NDEF message in one go. This would require
   too much RAM for a small microcontroller.

   Instead it is designed to output an I2C EEPROM, which is arranged into
   16-byte blocks. A maximum of 4 EEPROM blocks are written to or read from at a time.

.. feat:: Only static memory allocation is used.
   :id: CODEC_FEAT_8
   :status: open
   :links: CODEC_SPEC_4

   The stdio library needed for malloc takes a lot of available memory on the MSP430, so it is not used.
   The size of the circular buffer is fixed at compile time (move).

.. feat:: Encoder is written in C.
   :id: CODEC_FEAT_9
   :status: open
   :links: CODEC_SPEC_4

   There is little benefit to C++ given the low complexity of the encoder.

.. feat:: No RTOS is required
   :id: CODEC_FEAT_14
   :status: open
   :links: CODEC_SPEC_8, CODEC_SPEC_4

   An RTOS is not appropriate for this application. It will significantly increase the memory footprint.
   It will add complexity and make power consumption more difficult to control.

.. feat:: Time interval is conveyed in the URL.
   :id: CODEC_FEAT_10
   :status: complete
   :links: CODEC_SPEC_6, CODEC_SPEC_10

   The encoder will convert an integer time sample interval in minutes to a base64 string. Decoder
   performs the reverse operation.

.. feat:: The encoder only writes the full-length NDEF message once upon startup.
   :id: CODEC_FEAT_12
   :status: complete
   :links: CODEC_SPEC_2

   The entire NDEF message only needs to be written once upon startup. Afterwards, small
   parts of the message are modified at a time.

.. feat:: Frequently changing data are written to a circular buffer.
   :id: CODEC_FEAT_15
   :status: complete
   :links: CODEC_SPEC_2

   The list of environmental sensor readings (and its HMAC) will change at an interval of
   time interval minutes. If the time interval is set to 5 minutes, 100K writes will be
   reached in (5 minutes * 100e3) = 1 year.

   By using a circular buffer, these writes are distributed across many blocks. This is
   a form of `Wear levelling <https://en.wikipedia.org/wiki/Wear_leveling>`.

.. feat:: The encoder reads and writes a maximum of two circular buffer blocks at a time.
   :id: CODEC_FEAT_16
   :status: complete
   :links: CODEC_SPEC_4, CODEC_SPEC_2, CODEC_SPEC_8

   This reduces the requirement for RAM on the MSP430 and reduces power consumption (it takes time to write
   EEPROM blocks).

Status information
--------------------
.. feat:: The status string can be updated after startup.
   :id: CODEC_FEAT_11
   :status: complete
   :links: CODEC_SPEC_9

   After startup the status string will sometimes need to be updated. To do this, there should be a function for
   writing the first part few blocks in the NDEF message (up to the start of the circular buffer). It is
   intended that this function not be called frequently (once per day or less).
