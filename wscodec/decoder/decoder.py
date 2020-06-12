from .paramdecoder import ParamDecoder
from .exceptions import InvalidMajorVersionError
from datetime import timezone, datetime


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

        if majorversion == '1':
            self.params = ParamDecoder(circformat, timeintb64, statb64, circb64, secretkey, usehmac, self.scandatetime)
        else:
            raise InvalidMajorVersionError



