Features
=========

NDEF message
--------------

.. feat:: NDEF message type
   :id: CODEC_FEAT_1
   :links: CODEC_SPEC_1

   The message type is 0x03, corresponding to a known type.

.. feat:: NDEF message length
   :id: CODEC_FEAT_3
   :links: CODEC_SPEC_1

   The message length is 3 bytes. It cannot change after the message has been created.

NDEF record
--------------

.. feat:: Payload length
   :id: CODEC_FEAT_5
   :status: open
   :links: CODEC_SPEC_3

   Length of the NDEF record payload length in bytes. Similar to :need:`CODEC_FEAT_3`,
   it cannot change after the record has been created.

.. feat:: Type length
   :id: CODEC_FEAT_7
   :status: open
   :links: CODEC_SPEC_3

   Length of the :need:`CODEC_FEAT_8` field in bytes. This is 1 byte.

.. feat:: Record type
   :id: CODEC_FEAT_8
   :status: open
   :links: CODEC_SPEC_3

   NDEF record type is 0x55, which corresponds to a URI record.

Other
------

.. feat:: Base URL can be modified.
   :id: CODEC_FEAT_2
   :links: CODEC_SPEC_2

   The base URL can be changed. It is recommended to keep this as short as possible to
   allow more room for environmental sensor data.

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