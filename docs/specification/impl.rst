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
   converted to base64.

   The elapsed time is extracted in :any:`BufferDecoder.__init__` and converted back to an integer. 