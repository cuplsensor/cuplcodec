#  cuplcodec encodes environmental sensor data into a URL and the reverse.
#
#  https://github.com/cuplsensor/cuplcodec
#
#  Original Author: Malcolm Mackay
#  Email: malcolm@plotsensor.com
#  Website: https://cupl.co.uk
#
#  Copyright (C) 2021. Plotsensor Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from datetime import datetime
import pkg_resources
from .samples import SamplesURL
from .b64decode import B64Decoder
from .exceptions import InvalidMajorVersionError, InvalidFormatError
from . import hdc2021


def decode(secretkey: str,
           statb64: str,
           timeintb64: str,
           circb64: str,
           vfmtb64: str,
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

    vfmtb64: str
        Value of the URL parameter that contains the version and format string (base64 encoded).

    usehmac: bool
        True if the hash inside the circular buffer endstop is HMAC-MD5. False if it is MD5.

    scantimestamp: datetime
        The time that the tag was scanned. All decoded samples will be timestamped relative to this.

    Returns
    --------
    SamplesURL
        An object containing a list of timestamped environmental sensor samples.

    """

    encodermajorversion, formatcode = _get_encoderversion(vfmtb64)
    decodermajorversion = _get_decoderversion()

    if encodermajorversion != decodermajorversion:
        raise InvalidMajorVersionError(encodermajorversion, decodermajorversion)

    decoder = _get_decoder(formatcode)(statb64=statb64, timeintb64=timeintb64, circb64=circb64, usehmac=usehmac, secretkey=secretkey, scantimestamp=scantimestamp)
    return decoder


def _get_encoderversion(vfmtb64):
    vfmtb64 = vfmtb64[-4:]
    vfmtbytes = B64Decoder.b64decode(vfmtb64)
    encoderbytes = vfmtbytes[0:2]
    encoderversion = int.from_bytes(encoderbytes, byteorder='big')
    formatcode = vfmtbytes[2]
    return encoderversion, formatcode


def _get_decoderversion():
    decoderversionstr = pkg_resources.require("cuplcodec")[0].version
    decodermajorversion = int(decoderversionstr.split('.', 1)[0])
    return decodermajorversion


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
        raise InvalidFormatError(formatcode)

    return decoder





