Implementation
================

.. impl:: Sample interval
   :id: CODEC_IMPL_1
   :status: complete
   :links: CODEC_FEAT_10, CODEC_FEAT_6

   The time interval between samples (in minutes) is defined in the global variable :cpp:member:`smplintervalmins`.

   :cpp:func:`ndef_writepreamble()` reads :cpp:member:`smplintervalmins` and converts it to a base64 string.

   Decoder method :any:`decode_timeinterval` converts this back to an integer.

.. impl:: Elapsed time
   :id: CODEC_IMPL_2
   :status: complete
   :links: CODEC_FEAT_26

   The function :cpp:func:`sample_updateendstop` alters the elapsed time field, independent of the rest of the URL.
   It is intended that this is called once for each minute after a sample is taken. Elapsed time (as an integer) is
   converted to base64 and written to the end stop.

   Base64 elapsed time is extracted in :any:`BufferDecoder` and converted back to an integer.

.. impl:: Buffer length in blocks
   :id: CODEC_IMPL_3
   :status: complete
   :links: CODEC_FEAT_23

   Buffer length is set at compile time with :c:macro:`BUFSIZE_BLKS`.

.. impl:: Length in samples
   :id: CODEC_IMPL_4
   :status: complete
   :links: CODEC_FEAT_25

   The function :cpp:func:`sample_push` uses integer :cpp:member:`lensmpls` to record how many valid samples
   are in the circular buffer. When an octet is overwritten, it is reduced by :c:macro:`SAMPLES_PER_OCTET`.
   Otherwise it is incremented by one.

.. impl:: MD5
   :id: CODEC_IMPL_5
   :status: complete
   :links: CODEC_FEAT_24

   The encoder maintains :cpp:member:`samplehistory`, a RAM-based shadow of the EEPROM circular buffer.
   It consumes a lot of RAM, but this is unavoidable.

   On each call to :cpp:func:`sample_push`, the sample is appended to :cpp:member:`samplehistory` by
   :cpp:func:`smplhist_push`. The hash (MD5 or HMAC) is calculated with :cpp:func:`smplhist_md5`.
   This outputs a 9 byte structure (:cpp:type:`md5len_t`). It is converted to base64 (:cpp:member:`md5lenb64`)
   before it is written to the endstop octets (:need:`CODEC_SPEC_13`).