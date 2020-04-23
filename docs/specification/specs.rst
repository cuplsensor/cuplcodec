Specifications
===============

.. spec:: Message format
   :id: CODEC_SPEC_1
   :links: CODEC_REQ_1

   The message format is NDEF. This is used to transmit data to a phone using NFC.
   An NDEF message has 3 fields: Type, Length and Value.

   +-----------+------------------------+----------------------+----------------------+
   | NDEF Msg. | :need:`CODEC_FEAT_1`   | :need:`CODEC_FEAT_3` | Value                |
   +-----------+------------------------+------+-----+---------+----------------------+
   | Byte      | 0                      | 1    | 2   | 3       | 4...                 |
   +-----------+------------------------+------+-----+---------+----------------------+
   | Data      | 0x03                   | 0xFF | MSB | LSB     | :need:`CODEC_SPEC_3` |
   +-----------+------------------------+------+-----+---------+----------------------+

.. spec:: NDEF URL record
   :id: CODEC_SPEC_3
   :links: CODEC_SPEC_1
   :status: open

   Sensor data are stored in a URL record. As it is the only one in the message and of a known type,
   a phone opens the URL automatically in its default web browser.

   **NDEF record header**

   +-----------+----------------------+----------------------+-------------------------------+----------------------+
   | Desc      | :need:`CODEC_SPEC_5` | :need:`CODEC_FEAT_7` | :need:`CODEC_FEAT_5`          | :need:`CODEC_FEAT_8` |
   +-----------+----------------------+----------------------+-------+-------+-------+-------+----------------------+
   | Byte      | 0                    | 1                    | 2     | 3     | 4     | 5     | 6                    |
   +-----------+----------------------+----------------------+-------+-------+-------+-------+----------------------+
   | Data      |                      | 0x01                 | PL[3] | PL[2] | PL[1] | PL[0] | 0x55                 |
   +-----------+----------------------+----------------------+-------+-------+-------+-------+----------------------+

   **NDEF record payload start**

   +-----------+------------+------+------+------+-------------------+-------------+
   | Desc.     | URL Prefix | `Base URL`_        |  `Time interval`_ | `Serial`_   |
   +-----------+------------+------+------+------+-------------------+-------------+
   | Data      | 0x03       | t.plotsensor.com   |  /?t=AWg*         | &s=YWJjZGVm |
   +-----------+------------+------+------+------+-------------------+-------------+

   **NDEF record payload continued**

   +-----------+-------------+-------------+--------------------+-----------------+
   | Desc.     | `Version`_  | `Status`_   | CircBufferStart    | Circular Buffer |
   +-----------+-------------+-------------+--------------------+-----------------+
   | Data      | &v=01       | &x=AAABALEK | &q=                | MDaWMDaW...     |
   +-----------+-------------+-------------+--------------------+-----------------+

.. spec:: TNF + flags
   :id: CODEC_SPEC_5
   :links: CODEC_SPEC_3

   TNF and flags for the NDEF record.

.. spec:: Features for low memory utilisation
   :id: CODEC_SPEC_4
   :status: open
   :links: CODEC_REQ_5

.. spec:: Features to reduce memory wear
   :id: CODEC_SPEC_2
   :status: open
   :links: CODEC_REQ_8

.. spec:: Features for low power consumption
   :id: CODEC_SPEC_8
   :status: open
   :links: CODEC_REQ_9

.. spec:: Zero user configuration
   :id: CODEC_SPEC_6
   :links: CODEC_REQ_7

   The encoder must run without input from the user. This includes after the Power-on-Reset
   when a battery is replaced.

.. spec:: URL stores all required data.
   :id: CODEC_SPEC_7
   :links: CODEC_REQ_10

   All data required by the decoder must be conveyed in the URL. This includes the time interval
   between samples, the circular buffer format and the encoder version number.

.. spec:: URL status information
   :id: CODEC_SPEC_9
   :links: CODEC_REQ_11

   Status information will include
   1. State of the circular buffer (how many times it has looped back to the start).
   2. Battery voltage
   3. Cause of the most recent microcontroller reset
   4. Total number of resets (this may eventually loop back to 0).

.. spec:: Circular buffer decoding and timestamping
   :id: CODEC_SPEC_10
   :links: CODEC_REQ_2

   1. Circular buffer is unwrapped. Samples are put in order of recency.
   2. Minutes elapsed since the most recent sample is extracted from the URL.
   3. Current time (now in UTC) is determined.
   4. The first sample is assigned a timestamp = now - minutes elapsed.
   5. Minutes between samples is extracted from the URL. This is used to timestamp each sample
   relative to the first.

