from datetime import timezone, datetime
from .exceptions import InvalidCircFormatError, NoCircularBufferError, DelimiterNotFoundError, InvalidMajorVersionError
from .statdecoder import StatDecoder
from .htbufferdecoder import HTBufferDecoder
from .tbufferdecoder import TBufferDecoder
from .b64decode import b64decode



class Decoder:
    """
    Construct a Decoder object

    Parameters
    -----------
    secretkey:
        HMAC secret key as a string. Normally 16 bytes.

    statb64:
        Value of the URL parameter that holds status information (after base64 encoding).

    timeintb64:
        Value of the URL parameter that holds the time interval in minutes (after base64 encoding).

    circb64:
        Value of the URL parameter that contains the circular buffer of base64 encoded samples.

    ver:
        Value of the URL parameter that contains the version string.

    usehmac:
        True if the hash inside the circular buffer endstop is HMAC-MD5. False if it is MD5.

    scandatetime:
        The time that the tag was scanned. All decoded samples will be timestamped relative to this.

    """
    def __init__(self, secretkey: str, statb64: str, timeintb64: str, circb64: str, ver: str, usehmac: bool = True, scandatetime: datetime = None):
        majorversion = ver[-2:-1]
        circformat = ver[-1:]

        self.majorversion = majorversion
        self.scandatetime = scandatetime or datetime.now(timezone.utc)

        if majorversion != '1':
            raise InvalidMajorVersionError

        if circformat == '1':
            bufferdecoder = HTBufferDecoder
        elif circformat == '2':
            bufferdecoder = TBufferDecoder
        else:
            raise InvalidCircFormatError(circformat)

        self.circformat = circformat
        self.timeintervalmins = Decoder.decode_timeinterval(timeintb64)
        self.status = StatDecoder(statb64)
        try:
            self.buffer = bufferdecoder(circb64, self.timeintervalmins, secretkey, self.status, usehmac, self.scandatetime)
        except DelimiterNotFoundError:
            raise NoCircularBufferError(self.status)

    @staticmethod
    def decode_timeinterval(timeintb64):
        """
        Get the time interval in minutes from a URL parameter.

        Parameters
        -----------
        timeintb64
            Time interval between samples in minutes, little endian byte order and encoded as base64.

        Returns
        --------
        int
            Time interval between samples in minutes

        """
        timeintbytes = b64decode(timeintb64)
        timeint = int.from_bytes(timeintbytes, byteorder='little')
        return timeint



