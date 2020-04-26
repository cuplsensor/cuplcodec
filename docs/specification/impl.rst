Implementation
================

.. impl:: Sample interval
   :id: CODEC_IMPL_1
   :status: complete
   :links: CODEC_FEAT_10, CODEC_FEAT_6

   Set the sample interval in minutes in the :cpp:member:`smplintervalmins` member of the :cpp:member:`nv`
   struct.

   :cpp:func:`ndef_writepreamble()` reads :cpp:member:`smplintervalmins` and converts it to a base64 string.

   :meth:`decode_timeinterval` takes the base64 encoded sample interval and converts it back into
   an integer.

