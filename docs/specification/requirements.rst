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

    .. uml::
       :scale: 50 %
       :align: left

       @startuml
       skinparam componentStyle uml2

       interface "sample.h" as SMPL
       interface "nvstruct" as NV
       interface "nt3h.h" as NT3H

       SMPL -- [Encoder]
       NV -- [Encoder]

       [Encoder] --( NT3H
       @enduml

.. req:: Decoder parses URL parameters
   :id: CODEC_REQ_2
   :status: open
   :links: CODEC_REQ_3

   The decoder performs the reverse operation of the encoder. It takes parameters from the URL
   and returns environmental sensor data and metadata from them.

.. req:: The NDEF message is customisable.
   :id: CODEC_REQ_4
   :status: open
   :links: CODEC_REQ_1

.. req:: Encoder must run on a low cost MSP430.
   :id: CODEC_REQ_5
   :status: open

   The encoder must run with minimal resources and without an RTOS.

.. req:: Encoder does not require an absolute timestamp
   :id: CODEC_REQ_7
   :status: complete
   :links: CODEC_REQ_1

   The base URL output from the encoder does not feature an absolute timestamp.