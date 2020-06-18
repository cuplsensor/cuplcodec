from datetime import datetime
from .exceptions import InvalidMajorVersionError, InvalidCircFormatError
from . import hdc2021


def decode(secretkey: str, statb64: str, timeintb64: str, circb64: str, ver: str, usehmac: bool = True, scandatetime: datetime = None):
    """
       Decode the version string and extract codec version and format code. Raise an error if the codec version does not
       match. The format code is used to select the decoder to return. An error is raised if no decoder is available for
       the given code.

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
    majorversion = int(ver[-2:-1])
    formatcode = int(ver[-1:])

    if majorversion != 1:
        raise InvalidMajorVersionError

    decoder = _get_decoder(formatcode)(statb64, timeintb64, circb64, usehmac, secretkey, scandatetime)
    return decoder


def _get_decoder(formatcode: int):
    """
        Parameters
        -----------
        formatcode:
            Value of the codec format field. Specifies which decoder shall be used.

        Return
        -------
        A decoder class for the given format code.

        """
    decoders = {
        1: hdc2021.TempRH_URL,
        2: hdc2021.Temp_URL
    }
    try:
        decoder = decoders[formatcode]
    except KeyError:
        raise InvalidCircFormatError(formatcode)

    return decoder





