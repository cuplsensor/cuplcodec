from datetime import datetime
from .samples import SamplesURL
from .exceptions import InvalidMajorVersionError, InvalidCircFormatError
from . import hdc2021


def decode(secretkey: str,
           statb64: str,
           timeintb64: str,
           circb64: str,
           ver: str,
           usehmac: bool = True,
           scantimestamp: datetime = None) -> SamplesURL:
    """
    Decode the version string and extract codec version and format code. An error is raised if the codec version does
    not match. A decoder object is returned based on the format code. An error is raised if no decoder is available
    for the code.

    Parameters
    -----------
    secretkey: str
        HMAC secret key as a string. Normally 16 characters long.

    statb64: str
        Value of the URL parameter that holds status information (base64 encoded).

    timeintb64: str
        Value of the URL parameter that holds the time interval between samples in minutes (base64 encoded).

    circb64: str
        Value of the URL parameter that contains the circular buffer of base64 encoded samples.

    ver: str
        Value of the URL parameter that contains the version string (base64 encoded).

    usehmac: bool
        True if the hash inside the circular buffer endstop is HMAC-MD5. False if it is MD5.

    scantimestamp: datetime
        The time that the tag was scanned. All decoded samples will be timestamped relative to this.

    Returns
    --------
    SamplesURL
        An object containing a list of timestamped environmental sensor samples.

    """
    majorversion = int(ver[-2:-1])
    formatcode = int(ver[-1:])

    if majorversion != 1:
        raise InvalidMajorVersionError

    decoder = _get_decoder(formatcode)(statb64=statb64, timeintb64=timeintb64, circb64=circb64, usehmac=usehmac, secretkey=secretkey, scantimestamp=scantimestamp)
    return decoder


def _get_decoder(formatcode: int):
    """
        Parameters
        -----------
        formatcode:
            Value of the codec format field. Specifies which decoder shall be returned.

        Return
        -------
        Decoder class for the given format code.

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





