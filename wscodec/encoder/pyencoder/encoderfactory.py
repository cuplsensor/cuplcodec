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
