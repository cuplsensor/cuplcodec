from datetime import datetime
from .exceptions import InvalidMajorVersionError, InvalidCircFormatError
from .hdc2021 import HDC2021DecoderHT, HDC2021DecoderT


class DecoderFactory:
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
    @classmethod
    def decode(cls, secretkey: str, statb64: str, timeintb64: str, circb64: str, ver: str, usehmac: bool = True, scandatetime: datetime = None):
        majorversion = int(ver[-2:-1])
        formatcode = int(ver[-1:])

        if majorversion != 1:
            raise InvalidMajorVersionError

        decoder = cls.get_decoder(formatcode)(statb64, timeintb64, circb64, usehmac, secretkey, scandatetime)
        decoder.decode()
        return decoder

    @classmethod
    def get_decoder(cls, formatcode: int):
        """
            Construct a Decoder object

            Parameters
            -----------
            formatcode:
                Value of the codec format field. Specifies which decoder shall be used.

        """
        decoders = {
            1: HDC2021DecoderHT,
            2: HDC2021DecoderT
        }
        try:
            decoder = decoders[formatcode]
        except KeyError:
            raise InvalidCircFormatError(formatcode)

        return decoder





