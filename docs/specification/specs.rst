Specifications
===============

.. spec:: Message format
   :id: CODEC_SPEC_1
   :links: CODEC_REQ_1

   The message format is NDEF. This is used to transmit data to a phone using NFC.
   An NDEF message has 3 fields: Type, Length and Value.

   +-----------+------------------------+----------------------+----------------------+
   | NDEF Msg. | :need:`CODEC_FEAT_1`   | :need:`CODEC_FEAT_2` | Value                |
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
   | Desc      | :need:`CODEC_SPEC_5` | :need:`CODEC_FEAT_4` | :need:`CODEC_FEAT_3`          | :need:`CODEC_FEAT_5` |
   +-----------+----------------------+----------------------+-------+-------+-------+-------+----------------------+
   | Byte      | 0                    | 1                    | 2     | 3     | 4     | 5     | 6                    |
   +-----------+----------------------+----------------------+-------+-------+-------+-------+----------------------+
   | Data      | 0xC3                 | 0x01                 | PL[3] | PL[2] | PL[1] | PL[0] | 0x55                 |
   +-----------+----------------------+----------------------+-------+-------+-------+-------+----------------------+

   **NDEF record payload start**

   +-----------+------------+------+------+------+-------------------+-------------+
   | Desc.     | URL Prefix | `Base URL`_        |  `Time interval`_ | `Serial`_   |
   +-----------+------------+------+------+------+-------------------+-------------+
   | Data      | 0x03       | t.plotsensor.com   |  /?t=AWg*         | &s=YWJjZGVm |
   +-----------+------------+------+------+------+-------------------+-------------+

   **NDEF record payload continued**

   +-----------+-------------+-------------+--------------------+-----------------------+
   | Desc.     | `Version`_  | `Status`_   | CircBufferStart    | :need:`CODEC_SPEC_12` |
   +-----------+-------------+-------------+--------------------+-----------------------+
   | Data      | &v=01       | &x=AAABALEK | &q=                | MDaWMDaW...           |
   +-----------+-------------+-------------+--------------------+-----------------------+

.. spec:: Circular Buffer
   :id: CODEC_SPEC_12
   :links: CODEC_SPEC_3

   The circular buffer starts on a block boundary and occupies an integer number of 16-byte blocks.

   1K of EEPROM is enough for 32 blocks.

   Only two blocks are edited in RAM and written to EEPROM in any transaction:

   +----------------------------+------------------------------+
   | Cursor Block               | Next Block                   |
   +---------------+------------+------------+-----------------+
   | Cursor Octet  | Endstop Octets (0,1)    | Oldest Octet    |
   +-------+-------+-------------------------+-----------------+
   | S1    | S0    |                         |  SN   | SN-1    |
   +---+---+---+---+-------------------------+--+----+----+----+
   |R3 |R2 |R1 |R0 |                         |RL|RL-1|RL-2|RL-3|
   +---+---+---+---+-------------------------+--+----+----+----+

   Blocks are subdivided into two 8-byte octets. Each octet holds 2 sensor samples.

   Each sample is a pair of base64 encoded sensor readings.

   New sensor readings are written to Cursor Octet. Each time this occurs, contents of the subsequent 2 endstop
   octets are updated.

   When Cursor Octet is full, the cursor and endstop are moved forward:

   +------------------------------+------------------------------+
   | Cursor Block                 | Next Block                   |
   +---------------+--------------+------------------------------+
   | Octet         | Cursor Octet | Endstop Octets (0,1)         |
   +-------+-------+-------+------+------------------------------+
   | S2    | S1    | S0    | Spad |                              |
   +---+---+---+---+---+---+------+------------------------------+
   |R5 |R4 |R3 |R2 |R1 |R0 |                                     |
   +---+---+---+---+---+---+-------------------------------------+

   The previous oldest octet is overwritten. Note there can be a gap between the most recent sample and
   the start of the endstop octets. This is zero padded. The padding will not be decoded because the number
   of valid samples in the buffer is included in the endstop.

.. spec:: TNF + flags
   :id: CODEC_SPEC_5
   :links: CODEC_SPEC_3

   TNF and flags for the NDEF record.

   +-------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+---+---+
   | Bit   | 7                       | 6                       | 5                       | 4                       | 3                       | 2                       | 1 | 0 |
   +=======+=========================+=========================+=========================+=========================+=========================+=========================+===+===+
   | Field | :need:`CODEC_FEAT_17`   | :need:`CODEC_FEAT_18`   | :need:`CODEC_FEAT_19`   | :need:`CODEC_FEAT_20`   | :need:`CODEC_FEAT_21`   | :need:`CODEC_FEAT_22`           |
   +-------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+---+---+
   | Data  | 1                       | 1                       | 0                       | 0                       | 0                       |  0x03                           |
   +-------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+---+---+


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

.. spec:: Circular buffer is decoded
   :id: CODEC_SPEC_10
   :links: CODEC_REQ_2

   The circular buffer is unwrapped and decoded. Each sample is given a timestamp.

