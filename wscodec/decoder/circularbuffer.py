from .b64decode import B64Decoder
from .status import Status
from .exceptions import DelimiterNotFoundError
from struct import unpack


class CircularBufferURL:
    """
    Base class for a cuplcodec URL.

    This includes at least a circular buffer with a long string of base64 encoded sample data and
    a short status field.

    Instantiation decodes the status string first. It contains error information from the microcontroller running
    the encoder.

    Next it locates the :ref:`ENDSTOP_BYTE` in the circular buffer string. Characters to its left are the newest.
    Characters to its right are the oldest. The circular buffer is unwrapped into a string where :ref:`ENDSTOP_BYTE` is
    the last character and the oldest data is in the first.

    The linearised buffer is further divided into two parts:
    The endstop string (including the endstop itself) are at the end. It contains metadata such as the number of
    samples in the payload. This is preceded by the payload string, which contains a list base64-encocded
    environmental sensor readings. These are in chronological order oldest-to-newest reading left-to-right.

    The decoding of the payload string is handled elsewhere.

    Parameters
        ----------
        statb64 : str
            Base64 encoded status string extract from a URL parameter.
        circb64 : str
            A long string containing base64 encoded samples that are organised as a circular buffer.

    """
    ELAPSED_LEN_BYTES = 4   #: Length of the endstop elapsed minutes field in bytes (including the endstop itself).
    ENDSTOP_LEN_BYTES = 16  #: Length of the endstop in bytes.
    ENDSTOP_BYTE = '~'      #: The last character in the endstop and the end of the circular buffer. Must be URL safe.

    def __init__(self, statb64: str, circb64: str = None):
        self.statb64 = statb64
        self.circb64 = circb64

        self._decode_status()
        self._linearise()

        # Separate the buffer endstop from the payload
        self.endstopstr = self.linearbuf[-self.ENDSTOP_LEN_BYTES:]
        self.payloadstr = self.linearbuf[:-self.ENDSTOP_LEN_BYTES]

        self._decode_endstop()

    def _linearise(self):
        """
        Linearise the circular buffer.

        The circular buffer is made linear by concatenating the two parts of the buffer
        either side of the end stop.
        """

        # Split query string at the end of the endstop marker.
        splitend = self.circb64.split(self.ENDSTOP_BYTE)

        if len(splitend) != 2:
            raise DelimiterNotFoundError(self.circb64, self.status)

        circbufstart = splitend[1]
        circbufend = splitend[0]

        self.endmarkerpos = len(circbufend)
        self.linearbuf = circbufstart + circbufend + self.ENDSTOP_BYTE

    def _decode_status(self):
        """
        Instantiate a Status object. This can be over-ridden by a child of this class
        if the Status data needs to change in future.
        """
        self.status = Status(self.statb64)

    def _decode_endstop(self):
        """
        Decode the circular buffer endstop. This can be over-ridden by a child of this class
        if the endstop data needs to change in future.
        """
        endstopstr = self.endstopstr

        assert len(endstopstr) == self.ENDSTOP_LEN_BYTES

        endstopstr = endstopstr.replace(self.ENDSTOP_BYTE, B64Decoder.RFC3548_PADDING_BYTE)

        # Extract elapsed minutes since the previous sample in minutes xxx~. Replace the '=' to make this valid base64.
        elapsedb64 = endstopstr[-self.ELAPSED_LEN_BYTES:]
        # The remaining 12 bytes contain the MD5 hash and the number of valid pairs
        hashnb64 = endstopstr[:-self.ELAPSED_LEN_BYTES]

        # Decode elapsedb64
        elapsedbytes = B64Decoder.b64decode(elapsedb64)
        # Decode hashnb64
        hashn = B64Decoder.b64decode(hashnb64)

        # Extract the number of samples and the HMAC/MD5 checksum from the endstop.
        npairsbytes = hashn[7:9]
        hashbytes = hashn[0:7]

        self.elapsedmins = int.from_bytes(elapsedbytes, byteorder='little')
        self.npairs = unpack(">H", npairsbytes)[0]
        self.hash = hashbytes.hex()


