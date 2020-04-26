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
   converted to base64 and written to the t parameter.

   The t parameter is extracted in :any:`BufferDecoder` and converted back to an integer.

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