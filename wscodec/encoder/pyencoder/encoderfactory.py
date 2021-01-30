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
from .instrumented import InstrumentedSampleT, InstrumentedSampleTRH, InstrumentedSample


def encode(format,
           serial,
           secretkey,
           baseurl,
           smplintervalmins,
           resetsalltime,
           batteryadc,
           resetcause,
           usehmac,
           httpsdisable,
           tagerror) -> InstrumentedSample:
    """
    Python-wrapped encoder factory.

    Returns
    --------
    InstrumentedSample
        An object containing a list of timestamped environmental sensor samples.

    """

    encoder = _get_encoder(format)(serial=serial,
                                   secretkey=secretkey,
                                   baseurl=baseurl,
                                   smplintervalmins=smplintervalmins,
                                   resetsalltime=resetsalltime,
                                   batteryadc=batteryadc,
                                   resetcause=resetcause,
                                   usehmac=usehmac,
                                   httpsdisable=httpsdisable,
                                   tagerror=tagerror,
                                   format=format)
    return encoder


def _get_encoder(format: int):
    """
        Parameters
        -----------
        formatcode:
            Value of the codec format field. Specifies which decoder shall be returned.

        Return
        -------
        Decoder class for the given format code.

        """
    encoders = {
        InstrumentedSampleTRH.FORMAT_HDC2021_TRH: InstrumentedSampleTRH,
        InstrumentedSampleT.FORMAT_HDC2021_TEMPONLY: InstrumentedSampleT
    }
    try:
        encoder = encoders[format]
    except KeyError:
        # We need to test sending an unsupported format code.
        encoder = encoders[InstrumentedSampleTRH.FORMAT_HDC2021_TRH]

    return encoder
