PSCodec
========

The codec comprises an encoder and a decoder. The former takes an array of
samples as an input and outputs a URL. The latter performs the reverse
operation; it takes the URL as an input and outputs an array of samples.

Timestamps
-----------

A feature of PSCodec is that each sample does not include an absolute timestamp.
There is an RTC on the PSHardware, but it is only used to measure
time intervals of one minute.

Without the requirement for absolute time,
the user is not burdened with setting it like they have to on a wristwatch
or a cooker.

Instead PSCodec provides all necessary information for sample timestamps
to be reconstructed based on:

* Now (UTC), the time the PSCodec URL is received by PSWebApp. This coincides
  with the time the sensor is scanned by a phone.

* `Minutes elapsed <Elapsed>`_. The time difference between Now (UTC) and when the most
  recent sample was taken.

* `Time interval`_ in minutes between samples. This is a constant time interval
  between all samples in the buffer.

The reconstructed timestamps will be accurate to within one minute, which is
sufficient for most datalogging applications.

Message Authentication
------------------------

The URL contains a Hash-Based-Message-Authentication-Code or HMAC. This is made by taking the MD5 checksum of some data,
concatenating this with a secret key (:cpp:member:`seckey`) and then taking the MD5 of the result.

At the provisioning stage, a random secret key is generated that is unique to each sensor. This is a shared secret:
it is stored both by the web application and in the sensor.

The encoder computes the HMAC every time a new sample is collected (i.e. for each call of sample_push).
When PSCodec decodes a capture, it verifies the HMAC. If this fails an error is raised. The web application can
respond by not storing the capture data and notifying the user with error 409.



NDEF Preamble
--------------

+-----------+------+------------------+-----------------------------------------------------------------------------+
| NDEF Msg. | Type | Length           | Value                                                                       |
+-----------+------+------------------+----------------------------------------------------------------+------------+
| NDEF Rec. |                         | Header                                                         | Payload    |
+-----------+------+------+-----+-----+--------+----------+---------------+----------------+-----------+------------+
|           |      |      |     |     | Rec Hdr| Type Len | `Payload Length`_              | Rec. Type | URL Prefix |
+-----------+------+------+-----+-----+--------+----------+-------+-------+-------+--------+-----------+------------+
| Byte      | 0    | 1    | 2   | 3   | 4      | 5        | 6     | 7     | 8     | 9      | 10        | 11         |
+-----------+------+------+-----+-----+--------+----------+-------+-------+-------+--------+-----------+------------+
| Data      | 0x03 | 0xFF | MSB | LSB |        | 0x01     | PL[3] | PL[2] | PL[1] | PL[0]  | 0x55      | 0x03       |
+-----------+------+------+-----+-----+--------+----------+---+---+---+---+-------+--------+-----------+------------+

.. _payload-length:
Payload Length
~~~~~~~~~~~~~~~
NDEF message length in bytes as a 32-bit value. MSB first.

URL Header
-----------

+-----------+------+------------------+-----------------------------------------------------------------------------+
| NDEF Msg. |  Value                                                                                                |
+-----------+------+------------------+-----------------------------------------------------------------------------+
| NDEF Rec. |  Payload                                                                                              |
+-----------+------+------+------+-------------------+-------------+-------------+-------------+--------------------+
| Desc.     | `Base URL`_        |  `Time interval`_ | `Serial`_   | `Version`_  | `Status`_   | CircBufferStart    |
+-----------+------+------+------+-------------------+-------------+-------------+-------------+--------------------+
| Data      | t.plotsensor.com   |  /?t=AWg*         | &s=YWJjZGVm | &v=01       | &x=AAABALEK | &q=                |
+-----------+------+------+------+-------------------+-------------+-------------+-------------+--------------------+

.. _base-url:

Base URL
~~~~~~~~~

See non-volatile parameter :cpp:member:`baseurl`.

.. _serial:

Serial
~~~~~~~

See non-volatile parameter :cpp:member:`serial`.

.. _time-interval:

Time interval
~~~~~~~~~~~~~~

Time interval between samples in minutes is base64 encoded. Whilst the encoded string is 4 bytes long, the last character
must always be a padding byte (an URL safe replacement for '='). Therefore the unencoded time interval can only be 2 bytes long.
This is to match with the format of the minutes `Elapsed`_ field.

It is programmed as non-volatile parameter :cpp:member:`smplintervalmins`.

.. _version:

Version
~~~~~~~~
The version parameter determines which :class:`.ParamDecoder` shall be used by :class:`.Decoder`:

* :c:macro:`TEMPONLY` :class:`.TDecoder` Two temperature measurands per sample seperated by `Time interval`_.
* :c:macro:`TEMPRH` :class:`.HTDecoder` Temperature and relative humidity measurands in a sample.

This is programmed as non-volatile parameter :cpp:member:`version`.

.. _status:

Status
~~~~~~~

+-------------+--------+--------+--------+---------+-----------+---------+
| Byte        | 0      | 1      | 2      | 3       | 4         | 5       |
+-------------+--------+--------+--------+---------+-----------+---------+
| Description | `LoopCount`_    | `ResetsAllTime`_ | `BatV`_   | `RstC`_ |
+-------------+-----------------+------------------+-----------+---------+

The status field is 6 bytes long unencoded. It corresponds to :cpp:member:`status`. After base64 encoding
this becomes 8 bytes long.

LoopCount
^^^^^^^^^^^

See :cpp:member:`loopcount`.

ResetsAllTime
^^^^^^^^^^^^^^

Number of times the microcontroller running the encoder has reset. Each reset causes a counter to be incremented in
non-volatile memory (:cpp:member:`resetsalltime`).

BatV
^^^^^

See :cpp:member:`batvoltage`.

RstC
^^^^^^

Reset condition

URL Circular Buffer
--------------------

The sample arrays are ordered from the most recent at the top (element 0) to the oldest.

Demis are placed onto a circular buffer.
The end of the buffer is marked by an endstop_. Immediately to the left of
the endstop is the demi containing the most recent sample data.
The demi to the right contains the oldest sample data.


Samples
~~~~~~~~

Each sample contains two 12-bit measurands. These are organised as follows

+-----------------+-------+-------+-----+
| **Byte**        | 0     | 1     | 2   |
+-----------------+-------+-------+-----+
| **Description** | M1MSB | M2MSB | LSB |
+-----------------+-------+-------+-----+

The encoder stores samples using the :cpp:type:`pair_t` type.

M1MSB
^^^^^^

Measurand 1 Most significant 8-bits (see :cpp:member:`m1Msb`).

M2MSB
^^^^^^

Measurand 2 Most significant 8-bits (see :cpp:member:`m2Msb`).

LSB
^^^^

The least signficant 4-bit nibbles of M1 and M2 (see :cpp:member:`Lsb`).


+-------------+---+---+---+---+---+---+---+---+
| Bit         | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
+-------------+---+---+---+---+---+---+---+---+
| Description | M1[3:0]       | M2[3:0]       |
+-------------+---------------+---------------+


Chunks
~~~~~~~

+-----------------+-------------------------------------------+
| **Chunk**       | 0                                         |
+-----------------+---------------------+---------------------+
| **Sample**      | 0                   | 1                   |
+-----------------+-------+-------+-----+-------+-------+-----+
| **Byte**        | 0     | 1     | 2   | 3     | 4     | 5   |
+-----------------+-------+-------+-----+-------+-------+-----+
| **Description** | M1MSB | M2MSB | LSB | M1MSB | M2MSB | LSB |
+-----------------+-------+-------+-----+-------+-------+-----+

Each 6-byte chunk contains two samples_.

The encoder starts at the oldest sample and groups input data into 6 byte chunks.
Byte 0 of the chunk contains the oldest data and Byte 5 contains the newest.
Each chunk contains two samples.

The chunk containing the most recent data can be partially full.
In this case it is padded with samples that contain '0'. The number of samples
is written to the Length field in the endstop of the URL.
With this information the decoder discards the samples used for padding.


Demis
~~~~~~~

+------------+---------------------------------------------------+
| Demi       | 0                                                 |
+------------+-------------------------+-------------------------+
| SampleB64  | 0                       | 1                       |
+------------+-----+------+------+-----+-----+------+------+-----+
| Byte       | 0   | 1    | 2    |  3  | 4   | 5    | 6    |  7  |
+------------+-----+------+------+-----+-----+------+------+-----+

6-byte chunks are base64 encoded into 8-byte demis. This is done using only URL-safe characters.

Blocks
~~~~~~~

+------------+-------------------------+
| Block      | 0                       |
+------------+------------+------------+
| Demi      | 0          | 1          |
+------------+-----+------+------+-----+
| SampleB64  | 0   | 1    | 2    |  3  |
+------------+-----+------+------+-----+

Each 16-byte block contains two demis_.

+------------+-------------------------+-------------------------+-------------------------+---------------------------+
| Block      | 0                       | 1                       | ...                     | MSGLEN-1                  |
+------------+------------+------------+------------+------------+------------+------------+--------------+------------+
| Demi       | 0          | 1          | 2          | 3          | ...        | ...        | ...          | 2*MSGLEN-1 |
+------------+------------+------------+------------+------------+------------+------------+--------------+------------+


Endstop
~~~~~~~~

+----------------------------+------------------------------+
| Cursor Block               | Next Block                   |
+---------------+------------+------------+-----------------+
| Newest Demi   | Endstop 1  | Endstop 2  | Oldest Demi     |
+---------------+------------+------------+-----------------+


The endstop marks the end of the circular buffer. It is 16-bytes wide and it can span 2 blocks as shown above.

Immediately to the left of the endstop is the Demi containing the most recent sample data.

The demi to the right contains the oldest sample data or zero padding if the buffer is not full.

+-------------+-------------------------------+--------------------------------------+
| Demi       | Endstop 0                     | Endstop 1                            |
+-------------+---+---+---+---+---+---+---+---+---+---+----+----+----+----+----+-----+
| Byte        | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15  |
+-------------+---+---+---+---+---+---+---+---+---+---+----+----+----+----+----+-----+
| Description | MD5Length_ b64                                  | Elapsed_ b64 | )   |
+-------------+-------------------------------------------------+--------------+-----+

_`Elapsed` (base64) and end marker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The minutes elapsed counter increments by 1 every minute after the previous sample
was collected. It resets to 0 when a new sample is collected.

The decoder uses it to determine to the nearest minute when samples were collected.

The unencoded minutes elapsed field is 16-bits wide. This is the same width
as the unencoded time interval in minutes field.

The minutes elapsed field occupies 4 bytes after base64 encoding, including one
padding byte. By convention this is 0x61 or '='.

The encoder replaces the padding byte with :c:macro:`ENDSTOP_BYTE`. This marks the last byte of the end stop.

The first step performed by the decoder is to locate :c:macro:`ENDSTOP_BYTE`. After it is
found, it can be replaced with an '=' before the minutes elapsed field is
decoded from base64 into its original 16-bit value.

_`MD5Length`
^^^^^^^^^^^^^

This is 9 bytes long unencoded and 12 bytes long encoded. The C structure to hold these data
:cpp:type:`md5len_t` is shown below:

+-------------+---+---+---+---+---+---+---+---+------------+
| Byte        | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8          |
+-------------+---+---+---+---+---+---+---+---+------------+
| Description | MD5_                      | LengthSamples_ |
+-------------+---------------------------+----------------+

MD5
____

Least significant 7 bytes of the MD5 checksum taken of all samples in the buffer.


LengthSamples
______________

The number of valid samples in the circular buffer. This is populated from :cpp:var:`lenpairs`.



