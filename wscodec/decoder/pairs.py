#  Copyright (c) Plotsensor Ltd. 2020.
from .circularbuffer import CircularBufferURL
from .exceptions import MessageIntegrityError
from .b64decode import B64Decoder
from typing import List
from enum import Enum
import hashlib
import hmac

BYTES_PER_PAIR = 3                                      #: The number of bytes in each decoded Pair.
BYTES_PER_PAIRB64 = 4                                   #: The number of bytes in each base64 encoded Pair.
PAIRS_PER_DEMI = 2                                      #: The number of pairs in each 8-byte demi.
BYTES_PER_DEMI = BYTES_PER_PAIRB64 * PAIRS_PER_DEMI     #: The number of bytes in each demi.


class HashType(Enum):
    MD5 = 1
    HMAC_MD5 = 2


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
    """
    This takes the payload of the linearised buffer, which is a long string of base64 characters. It decodes this
    into a list of pairs. The hash (MD5 or HMAC-MD5) is taken and compared with that supplied in the URL by the
    encoder. If the hashes match then the decode has been successful. If not, an exception is raised.

    Parameters
    ----------
    *args
        Variable length argument list.
    usehmac: bool
        True if the hash inside the circular buffer endstop is HMAC-MD5. False if it is MD5.
    secretkey: str
        HMAC secret key as a string. Normally 16 characters long.
    **kwargs
        Keyword arguments to be passed to parent class constructors.
    """
    def __init__(self, *args, usehmac: bool = False, secretkey: str = None,  **kwargs):
        super().__init__(*args, **kwargs)

        self._decode_pairs()
        self._verify(usehmac, secretkey)

    def _verify(self, usehmac : bool, secretkey : str):
        """
        Calculate a hash from the list of pairs according to the same algorithm used
        by the encoder (see :ref:`pairhist_hash`). Besides pairs, data from the status URL parameter
        are included. This makes it very unlikely that the same data will be hashed twice, as well as 'protecting'
        the status parameter from modification by a 3rd party.

        A fragment of the calculated hash is compared with that supplied by the encoder. If the hashes agree then
        verification is successful. If not, an exception is raised.

        Parameters
        ----------
        usehmac : bool
            True if the hash inside the circular buffer endstop is HMAC-MD5. False if it is MD5.
        secretkey : str
            HMAC secret key as a string. Normally 16 characters long.

        Raises
        -------
            MessageIntegrityError: If the hash calculated by this decoder does not match the hash provided by the encoder.

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
        calcHash, self.hashtype = self.__class__._gethash(pairhist, usehmac, secretkey)
        urlHash = self.hash

        # Truncate calculated MD5 to the same length as the URL MD5.
        calcHash = calcHash[0:len(urlHash)]

        if urlHash != calcHash:
            raise MessageIntegrityError(calcHash, urlHash)

        assert self.npairs == len(self.pairs)

    @staticmethod
    def _gethash(message: bytearray, usehmac: bool, secretkey: str):
        """
        Calculates the hash of a message.

        Parameters
        ----------
        message : bytearray
            Input data to the hashing algorithm.
        usehmac : bool
            When True the HMAC-MD5 algorithm is used. Otherwise MD5 is used (not recommended for production).
        secretkey : str
            HMAC secret key as a string. Normally 16 characters long.

        Returns
        -------
        digest : str
            The message hash.
        hashtype : HashType
            The hash algorithm used.

        """
        secretkeyba = bytearray(secretkey, 'utf8')
        if usehmac:
            hmacobj = hmac.new(secretkeyba, message, "md5")
            digest = hmacobj.hexdigest()
            hashtype = HashType.HMAC_MD5
        else:
            digest = hashlib.md5(message).hexdigest()
            hashtype = HashType.MD5
        return digest, hashtype

    def _decode_pairs(self):
        """
        The payload string is converted into a list of 8-byte demis (see :ref:`demi`).

        The first demi is the newest; its data have been written to the circular buffer most recently,
        so it closest to the left of the endstop. It can contain either one or two pairs.
        This is decoded first.

        Subsequent (older) demis each contain 2 pairs. These are decoded. The final list of pairs is in
        chronological order with the newest first and the oldest last.
        """
        self.pairs = list()

        # Convert payload string into 8 byte demis.
        demis = self._dividestring(self.payloadstr, BYTES_PER_DEMI)

        # The newest 8 byte demi might only contain 1 valid pair.
        # If so, it is a partial one so it gets processed first.
        partial = self.npairs % PAIRS_PER_DEMI
        full = int(self.npairs / PAIRS_PER_DEMI)

        if partial != 0:
            demi = demis.pop()
            pair = self._pairsfromdemi(demi)[1]  # Only append the oldest pair, for the newest is invalid.
            self.pairs.append(pair)

        # Process remaining full demis. These all contain 2 pairs.
        for i in range(0, full, 1):
            demi = demis.pop()
            demipairs = self._pairsfromdemi(demi)  # Append both pairs.
            self.pairs.extend(demipairs)

    @staticmethod
    def _dividestring(source: str, n: int):
        """

        Parameters
        ----------
        source : str
            The string to be divided.
        n
            The number of characters in each substring.

        Returns
        -------
        A list of substrings, each containing n characters.

        """
        return list(source[i:i+n] for i in range(0, len(source), n))

    def _pairsfromdemi(self, demi: str) -> List[Pair]:
        """
        Decode a demi into 2 pairs.

        Parameters
        ----------
        demi : str
            A string containing 8 base64 characters.

        Returns
        -------
        A list of 2 pairs:
            Element 0 is the oldest pair, decoded from the first 4 demi characters.
            Element 1 is the newest pair, decoded from the last 4 demi characters.

        """
        pairs = list()

        assert len(demi) == BYTES_PER_DEMI, demi

        for i in range(0, BYTES_PER_DEMI, BYTES_PER_PAIRB64):
            pairb64 = demi[i:i+BYTES_PER_PAIRB64]
            pair = Pair.from_b64(pairb64)
            pairs.append(pair)

        pairs.reverse()
        return pairs