Implementation
================

.. impl:: Sample interval
   :id: CODEC_IMPL_1
   :status: complete
   :links: CODEC_FEAT_10, CODEC_FEAT_6

   The time interval between samples (in minutes) is defined in the global variable :cpp:member:`smplintervalmins`.

   :cpp:func:`ndef_writepreamble()` converts :cpp:member:`smplintervalmins` into a base64 string and writes it
   to URL parameter 't'.

   Decoder method :any:`decode_timeinterval` converts this back to an integer.

.. impl:: Elapsed time
   :id: CODEC_IMPL_2
   :status: complete
   :links: CODEC_FEAT_26

   The function :cpp:func:`sample_updateendstop` alters the elapsed time field, independent of the rest of the URL.
   It is intended that this is called once for each minute after a sample is taken. Elapsed time (as an integer) is
   converted to base64 and written to the end stop.

   Base64 elapsed time is extracted in :any:`BufferDecoder` and converted back to an integer.

.. impl:: Length in blocks
   :id: CODEC_IMPL_3
   :status: complete
   :links: CODEC_FEAT_23

   Buffer length is set at compile time with :c:macro:`BUFSIZE_BLKS`.

.. impl:: Length in samples
   :id: CODEC_IMPL_4
   :status: complete
   :links: CODEC_FEAT_25

   The function :cpp:func:`sample_push` uses integer :cpp:member:`lenpairs` to record how many valid samples
   are in the circular buffer. When an demi is overwritten, it is reduced by :c:macro:`PAIRS_PER_DEMI`.
   Otherwise it is incremented by one. When the buffer is full :cpp:member:`lenpairs` will equal
   :cpp:member:`buflensamples`.

.. impl:: MD5
   :id: CODEC_IMPL_5
   :status: complete
   :links: CODEC_FEAT_24, CODEC_FEAT_40

   The encoder maintains :cpp:member:`samplehistory`, a RAM-based shadow of the EEPROM circular buffer.
   It consumes a lot of RAM, but this is unavoidable.

   On each call to :cpp:func:`sample_push`, the sample is appended to :cpp:member:`samplehistory` by
   :cpp:func:`pairhist_push`. The hash (MD5 or HMAC) is calculated with :cpp:func:`pairhist_md5`.
   This outputs a 9 byte structure (:cpp:type:`md5len_t`). It is converted to base64 (:cpp:member:`md5lenb64`)
   before it is written to the endstop demis (:need:`CODEC_SPEC_13`).

.. impl:: Append sample
   :id: CODEC_IMPL_6
   :status: complete
   :links: CODEC_FEAT_15

   Samples are added to the circular buffer with :cpp:func:`sample_push`. This takes one or two measurands,
   depending on the circular buffer format.

.. impl:: Initialisation
   :id: CODEC_IMPL_7
   :status: complete
   :links: CODEC_FEAT_12

   The NDEF message and its circular buffer are initialised with :cpp:func:`sample_init`. Given there are
   no samples in the circular buffer, the endstop and cursor are omitted. All demis are set to MDaW
   (all zeroes).

   State machines in the ``sample`` and ``demi`` files are reset.

.. impl:: Serial
   :id: CODEC_IMPL_8
   :status: complete
   :links: CODEC_FEAT_38

   The serial string is defined in the global variable :cpp:member:`serial`. This must be
   :c:macro:`SERIAL_LENBYTES` long. It must contain only URL-safe characters.

   :cpp:func:`ndef_writepreamble()` copies this into URL parameter 's'.