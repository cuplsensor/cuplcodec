from .circularbuffer import CircularBufferURL
from .exceptions import MessageIntegrityError
from .b64decode import B64Decoder
import hashlib
import hmac

BYTES_PER_PAIR = 3
BYTES_PER_PAIRB64 = 4
PAIRS_PER_DEMI = 2
BYTES_PER_DEMI = BYTES_PER_PAIRB64 * PAIRS_PER_DEMI


class Pair:
    """
    Class representing a pair of 12-bit sensor readings.

    In the URL each pair consists of a 4 byte (base64) string. These decode to 3 8-bit bytes. The last contains
    4-bits from reading0 and 4-bits from reading 1.

    When this class is instantiated, the 3 8-bit bytes are converted back into two 12-bit readings.

    Parameters
    ----------
    rd0MSB : int
        Most Signficant Byte of environmental sensor reading0.
    rd1MSB : int
        Most Significant Byte of environmental sensor reading1.
    Lsb : int
        Upper 4-bits are the least significant bits of reading0.
        Lower 4-bits are the least significant bits of reading1.
    """
    def __init__(self, rd0MSB: int, rd1MSB: int, Lsb: int):

        self.rd0MSB = rd0MSB
        self.rd1MSB = rd1MSB
        self.Lsb = Lsb

        rd0Lsb = (self.Lsb >> 4) & 0xF
        rd1Lsb = self.Lsb & 0xF
        self.rd0 = ((self.rd0MSB << 4) | rd0Lsb)
        self.rd1 = ((self.rd1MSB << 4) | rd1Lsb)

    def __repr__(self):
        """

        Returns
        -------
        A string containing both 12-bit readings.
        """
        return str(self.readings())

    @classmethod
    def from_bytes(cls, bytes: bytes):
        """

        Parameters
        ----------
        bytes : bytes
            The 3 bytes that make up a pair rd0MSB, rd1MSB and Lsb.

        Returns
        -------
        A pair instantiated from the 3 byte input.

        """
        assert len(bytes) == BYTES_PER_PAIR
        return cls(rd0MSB=bytes[0], rd1MSB=bytes[1], Lsb=bytes[2])

    @classmethod
    def from_b64(cls, pairb64: str):
        """

        Parameters
        ----------
        str4: str
            A 4 character string that represents a base64 encoded pair. These are extracted from the circular buffer.

        Returns
        -------
        A pair instantiated from the 4 character string.
        """
        assert len(pairb64) == BYTES_PER_PAIRB64
        pairbytes = B64Decoder.b64decode(pairb64)
        return cls.from_bytes(pairbytes)

    def readings(self):
        """

        Returns
        --------
        A dictionary containing both 12-bit readings.
        """
        return {'rd0': self.rd0, 'rd1': self.rd1}


class PairsURL(CircularBufferURL):
    def __init__(self, *args, usehmac: bool = False, secretkey: str = None,  **kwargs):
        """

        :param args:
        :param usehmac:
        :param secretkey:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.usehmac = usehmac
        self.secretkey = secretkey

        self._decode_pairs()
        self._verify()

    def _verify(self):
        """

        :return:
        """
        pairhist = bytearray()

        for pair in self.pairs:
            pairhist.append(pair.rd0MSB)
            pairhist.append(pair.rd1MSB)
            pairhist.append(pair.Lsb)

        pairhist.append(self.status.loopcount >> 8)
        pairhist.append(self.status.loopcount & 0xFF)
        pairhist.append(self.status.resetsalltime >> 8)
        pairhist.append(self.status.resetsalltime & 0xFF)
        pairhist.append(self.status.batv_resetcause >> 8)
        pairhist.append(self.status.batv_resetcause & 0xFF)
        pairhist.append(self.endmarkerpos >> 8)
        pairhist.append(self.endmarkerpos & 0xFF)

        # Perform message authentication.
        calcMD5 = self._gethash(pairhist)
        urlMD5 = self.urlMD5

        # Truncate calculated MD5 to the same length as the URL MD5.
        calcMD5 = calcMD5[0:len(urlMD5)]

        if urlMD5 != calcMD5:
            raise MessageIntegrityError(calcMD5, urlMD5)

        assert self.npairs == len(self.pairs)

    def _gethash(self, message):
        """

        :param message:
        :return:
        """
        secretkeyba = bytearray(self.secretkey, 'utf8')
        if self.usehmac:
            hmacobj = hmac.new(secretkeyba, message, "md5")
            digest = hmacobj.hexdigest()
        else:
            digest = hashlib.md5(message).hexdigest()
        return digest

    def _decode_pairs(self):
        """

        :return:
        """
        self.pairs = list()

        # Convert payload string into 8 byte demis.
        demis = self._chunkstring(self.payloadstr, BYTES_PER_DEMI)

        # The newest 8 byte chunk might only contain
        # 1 valid pair. If so, this is a
        # partial demi and it is processed first.
        rem = self.npairs % PAIRS_PER_DEMI
        full = int(self.npairs / PAIRS_PER_DEMI)

        if rem != 0:
            demi = demis.pop()
            pair = self._pairsfromdemi(demi)[1]
            self.pairs.append(pair)

        # Process remaining full demis. These all contain 2 pairs.
        for i in range(0, full, 1):
            demi = demis.pop()
            demipairs = self._pairsfromdemi(demi)
            self.pairs.extend(demipairs)

    def _chunkstring(self, string, n):
        return list(string[i:i+n] for i in range(0, len(string), n))

    # Obtain samples from a 4 byte base64 chunk. Chunk should be renamed to demi here.
    def _pairsfromdemi(self, demi):
        """

        :param demi:
        :return:
        """
        pairs = list()

        assert len(demi) == BYTES_PER_DEMI, demi

        for i in range(0, BYTES_PER_DEMI, BYTES_PER_PAIRB64):
            pairb64 = demi[i:i+BYTES_PER_PAIRB64]
            pair = Pair.from_b64(pairb64)
            pairs.append(pair)

        # Return newest sample first.
        pairs.reverse()
        return pairs