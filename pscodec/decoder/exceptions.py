class PSCodecError(Exception):
    """Base PSCodec error class."""

    def __init__(self):
        super().__init__()


class DecoderError(PSCodecError):
    """Decoder error class."""

    def __init__(self):
        super().__init__()


class InvalidMajorVersionError(DecoderError):
    """ Raised when there is no decoder for the supplied major version.  """

    def __init__(self):
        super().__init__()


class ParamDecoderError(PSCodecError):
    """ Raised when there is a problem decoding URL parameters. """

    def __init__(self):
        super().__init__()


class InvalidCircFormatError(ParamDecoderError):
    errormsg = " Invalid circular buffer format = {}. "

    def __init__(self, circformat):
        super().__init__()
        self.circformat = circformat

    def __str__(self):
        return self.errormsg.format(self.circformat)


class NoCircularBufferError(ParamDecoderError):
    errormsg = " No circular buffer to decode. There is an error with the microcontroller. "

    def __init__(self, status):
        super().__init__()
        self.status = status