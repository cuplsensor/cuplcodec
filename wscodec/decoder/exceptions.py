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


class CircularBufferError(PSCodecError):
    """Base application error class."""

    def __init__(self):
        super().__init__()


class MessageIntegrityError(CircularBufferError):
    errormsg = "MD5 checksum mismatch. Calculated MD5 = {}, URL MD5 = {}"

    def __init__(self, calcmd5, urlmd5):
        super().__init__()
        self.calcmd5 = calcmd5
        self.urlmd5 = urlmd5

    def __str__(self):
        return self.errormsg.format(self.calcmd5, self.urlmd5)


class DelimiterNotFoundError(CircularBufferError):
    errormsg = " No delimiting character found in the circular buffer string = {}. "

    def __init__(self, encstr):
        super().__init__()
        self.encstr = encstr

    def __str__(self):
        return self.errormsg.format(self.encstr)