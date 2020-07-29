class DecoderError(Exception):
    """cupl Decoder error class."""

    def __init__(self):
        super().__init__()


class InvalidMajorVersionError(DecoderError):
    """ Raised when there is no decoder for the supplied major version.  """

    def __init__(self):
        super().__init__()


class InvalidFormatError(DecoderError):
    errormsg = " Invalid circular buffer format = {}. "

    def __init__(self, circformat, status):
        super().__init__()
        self.circformat = circformat
        self.status = status

    def __str__(self):
        return self.errormsg.format(self.circformat)


class MessageIntegrityError(DecoderError):
    errormsg = "MD5 checksum mismatch. Calculated MD5 = {}, URL MD5 = {}"

    def __init__(self, calcmd5, urlmd5):
        super().__init__()
        self.calcmd5 = calcmd5
        self.urlmd5 = urlmd5

    def __str__(self):
        return self.errormsg.format(self.calcmd5, self.urlmd5)


class DelimiterNotFoundError(DecoderError):
    errormsg = " No delimiting character found in the circular buffer string = {}. There is an error with the microcontroller. "

    def __init__(self, circb64, status):
        super().__init__()
        self.circb64 = circb64
        self.status = status

    def __str__(self):
        return self.errormsg.format('circb64='+self.circb64+' status='+self.status)