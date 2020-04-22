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

.. feat:: No absolute timestamp
   :id: CODEC_FEAT_6
   :status: complete
   :links: CODEC_SPEC_6

   The base URL output from the encoder does not feature an absolute timestamp.

.. feat:: Base URL can be modified.
   :id: CODEC_FEAT_7
   :links: CODEC_SPEC_2

   The base URL can be changed. It is recommended to keep this as short as possible to
   allow more room for environmental sensor data.

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

.. feat:: Time interval is conveyed in the URL.
   :id: CODEC_FEAT_10
   :status: complete
   :links: CODEC_SPEC_6

   The encoder will convert an integer time sample interval in minutes to a base64 string. Decoder
   performs the reverse operation.

.. feat:: The status string can be updated after startup.
   :id: CODEC_FEAT_11

   After startup the status string will sometimes need to be updated. To do this, there should be a function for
   writing the first part few blocks in the NDEF message (up to the start of the circular buffer). It is
   intended that this function not be called frequently (once per day or less).


.. feat:: The encoder only writes the full-length NDEF message once upon startup.
   :id: CODEC_FEAT_12
   :status: complete
   :links: CODEC_REQ_1

   To minimise power consumption and reduce flash wear, the entire NDEF message is written once.

.. feat:: Frequently changing data are written to a circular buffer.

.. feat:: The encoder reads and writes a maximum of two circular buffer blocks at a time.
   :id: CODEC_FEAT_13

   This reduces the requirement for RAM on the MSP430 and reduces power consumption (it takes time to write
   EEPROM blocks).
