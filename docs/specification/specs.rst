Specifications
===============

.. |64| replace:: \ :sub:`64`\

.. spec:: Message format
   :id: CODEC_SPEC_1
   :links: CODEC_REQ_1
   :status: complete

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
   :status: complete

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

   +-----------+------------+------+------+--------+------------------------+-------------------------+
   | Desc.     | URL Prefix | :need:`CODEC_FEAT_7` |  :need:`CODEC_FEAT_10` |  :need:`CODEC_FEAT_38`  |
   +-----------+------------+------+------+--------+------------------------+-------------------------+
   | Data      | 0x03       | t.plotsensor.com     |  /?t=AWg*              | &s=YWJjZGVm             |
   +-----------+------------+------+------+--------+------------------------+-------------------------+

   **NDEF record payload continued**

   +-----------+------------------------+-----------------------+--------------------+-----------------------+
   | Desc.     | :need:`CODEC_SPEC_18`  | :need:`CODEC_SPEC_15` | CircBufferStart    | :need:`CODEC_SPEC_12` |
   +-----------+------------------------+-----------------------+--------------------+-----------------------+
   | Data      | &v=AAAA                | &x=AAABALEK           | &q=                | MDaWMDaW...           |
   +-----------+------------------------+-----------------------+--------------------+-----------------------+

.. spec:: Circular Buffer
   :id: CODEC_SPEC_12
   :status: complete
   :links: CODEC_SPEC_3, CODEC_SPEC_2

   The circular buffer starts on a block boundary and occupies an integer number of 16-byte blocks.
   1K of EEPROM is enough for 32 blocks.

   Only two blocks are edited in RAM at a time:

   +------------------------------------------------+--------------------------------------------------------------------------+
   | Cursor Block                                   | Next Block                                                               |
   +-----------------------------------+------------+--------------------------------+-----------------------------------------+
   | Cursor Octet                      | Endstop Octets (0,1)                        | Oldest Octet                            |
   +-----------------+-----------------+---------------------------------------------+-------------------+---------------------+
   | P|64|1          | P|64|0|         |                                             |  P|64|N           | P|64|N-1            |
   +--------+--------+--------+--------+---------------------------------------------+--------+----------+----------+----------+
   | R|64|3 | R|64|2 | R|64|1 | R|64|0 |                                             | R|64|L | R|64|L-1 | R|64|L-2 | R|64|L-3 |
   +--------+--------+--------+--------+---------------------------------------------+--------+----------+----------+----------+

   Blocks are subdivided into two 8-byte octets. Each octet holds 2 base64 encoded pairs.

   Each pair consists of 2 base64 encoded sensor readings. By default these will be captured
   simultaneously by a temperature sensor and a humidity sensor.

   New sensor readings are written to Cursor Octet. Each time this occurs, the subsequent
   :need:`CODEC_SPEC_13` is updated.

   When Cursor Octet is full, both it and the endstop are moved forward when the next sensor reading is added:

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

.. spec:: Endstop
   :id: CODEC_SPEC_13
   :status: complete
   :links: CODEC_SPEC_12

   The endstop occupies 2 octets (16 bytes) after the cursor octet. It is terminated with a unique character. This marks
   the end of the circular buffer; the divide between new and old data. The decoder finds this in order to unwrap the circular buffer into a list of samples,
   ordered newest to oldest.

   +-------------+-------------------------------+-----------------------------------------------+
   | Octet       | Endstop 0                     | Endstop 1                                     |
   +-------------+---+---+---+---+---+---+---+---+---+---+----+----+----+----+-------------+-----+
   | Byte        | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14          | 15  |
   +-------------+---+---+---+---+---+---+---+---+---+---+----+----+----+----+-------------+-----+
   | Description | :need:`CODEC_SPEC_14`                           | :need:`CODEC_SPEC_17` | )   |
   +-------------+-------------------------------------------------+-----------------------+-----+

   The endstop contains data about the current state of the circular buffer, for example the number of
   valid samples it contains. These data are appended to the circular buffer to meet
   :need:`CODEC_SPEC_2`.

.. spec:: VFmt b64
   :id: CODEC_SPEC_18
   :status: open
   :links: CODEC_SPEC_3

   This is a 3 byte structure that expands to 4 bytes after base64 encoding.

   The unencoded structure is:

   +-------------+-----------+-----------+-----------------------+
   | Byte        | 0         | 1         |  2                    |
   +-------------+-----------+-----------+-----------------------+
   | Description | :need:`CODEC_FEAT_41` | :need:`CODEC_FEAT_42` |
   +-------------+-----------------------+-----------------------+

.. spec:: MD5Length b64
   :id: CODEC_SPEC_14
   :status: complete
   :links: CODEC_SPEC_13

   This is a 9 byte structure that expands to 12 bytes after base64 encoding.

   The unencoded structure is:

   +-------------+---+---+---+---+---+---+---+---+-------------------+
   | Byte        | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8                 |
   +-------------+---+---+---+---+---+---+---+---+-------------------+
   | Description | :need:`CODEC_FEAT_24`     | :need:`CODEC_FEAT_25` |
   +-------------+---------------------------+-----------------------+

.. spec:: Status b64
   :id: CODEC_SPEC_15
   :status: complete
   :links: CODEC_SPEC_3

   This is a 6 byte structure that expands to 8 bytes after base64 encoding.

   It corresponds to :cpp:member:`status`. Status information is used by the decoder
   to determine if the encoder and its microcontroller host are running ok.

   The unencoded structure is:

   +-------------+--------+--------------+--------+--------------+-----------------------+-----------------------+
   | Byte        | 0      | 1            | 2      | 3            | 4                     | 5                     |
   +-------------+--------+--------------+--------+--------------+-----------------------+-----------------------+
   | Description | :need:`CODEC_FEAT_28` | :need:`CODEC_FEAT_29` | :need:`CODEC_FEAT_30` | :need:`CODEC_SPEC_16` |
   +-------------+-----------------------+-----------------------+-----------------------+-----------------------+

.. spec:: ResetCause
   :id: CODEC_SPEC_16
   :status: complete
   :links: CODEC_SPEC_15

   Flags to indicate causes of the most recent microcontroller reset.

   +-------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
   | Bit         | 0                     | 1                     | 2                     | 3                     | 4                     | 5                     | 6                     | 7                     |
   +-------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
   | Description | :need:`CODEC_FEAT_31` | :need:`CODEC_FEAT_32` | :need:`CODEC_FEAT_33` | :need:`CODEC_FEAT_34` | :need:`CODEC_FEAT_35` | :need:`CODEC_FEAT_36` |                       | :need:`CODEC_FEAT_37` |
   +-------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+

.. spec:: TNF + flags
   :id: CODEC_SPEC_5
   :status: complete
   :links: CODEC_SPEC_3

   TNF and flags for the NDEF record.

   +-------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+---+---+
   | Bit   | 7                       | 6                       | 5                       | 4                       | 3                       | 2                       | 1 | 0 |
   +=======+=========================+=========================+=========================+=========================+=========================+=========================+===+===+
   | Field | :need:`CODEC_FEAT_17`   | :need:`CODEC_FEAT_18`   | :need:`CODEC_FEAT_19`   | :need:`CODEC_FEAT_20`   | :need:`CODEC_FEAT_21`   | :need:`CODEC_FEAT_22`           |
   +-------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+---+---+
   | Data  | 1                       | 1                       | 0                       | 0                       | 0                       |  0x03                           |
   +-------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+---+---+


.. spec:: Low memory utilisation
   :id: CODEC_SPEC_4
   :status: open
   :links: CODEC_REQ_12

   The encoder must use <2K of RAM and <16K of non-volatile FRAM, as can be found on an
   MSP430FR2033 microcontroller.

.. spec:: Reduce EEPROM wear
   :id: CODEC_SPEC_2
   :status: open
   :links: CODEC_REQ_8

.. spec:: Low power consumption
   :id: CODEC_SPEC_8
   :status: open
   :links: CODEC_REQ_12

   The encoder will run for >2 years on a hardware powered by a CR1620 battery.

.. spec:: Zero user configuration
   :id: CODEC_SPEC_6
   :links: CODEC_REQ_7

   The encoder must run without input from the user. This includes after the Power-on-Reset
   when a battery is replaced.

.. spec:: URL parameters decoded
   :id: CODEC_SPEC_19
   :links: CODEC_REQ_2

   Before the circular buffer is decoded, URL parameters such as :need:`CODEC_SPEC_18` are needed.

.. spec:: Circular buffer decoded
   :id: CODEC_SPEC_10
   :links: CODEC_SPEC_19

   The decoder outputs a list of samples from the URL. Output
   depends on :need:`CODEC_FEAT_42`. By default samples will contain temperature
   and humidity readings, converted to degrees C and percent respectively.
   Each will have a timestamp precise to one minute.
   This corresponds to the time that the sample was added to the circular buffer.

