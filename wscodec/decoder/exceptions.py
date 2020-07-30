# Helpful: https://julien.danjou.info/python-exceptions-guide/

class DecoderError(Exception):
    """Base cupl Decoder error class."""

    def __init__(self, msg="cupl Decoder Error"):
        super().__init__(msg)


class InvalidMajorVersionError(DecoderError):
    def __init__(self, encoderversion, decoderversion, msg=None):
        if msg is None:
            # Set a default error messasge
            msg = "There is a mismatch between the encoder version = {} " \
                  "and decoder version = {} ".format(encoderversion, decoderversion)
        super().__init__(msg)
        self.encoderversion = encoderversion
        self.decoderversion = decoderversion


class InvalidFormatError(DecoderError):
    def __init__(self, circformat, msg=None):
        if msg is None:
            # Set a default error message
            msg = "Invalid circular buffer format = {}.".format(circformat)
        super().__init__(msg)
        self.circformat = circformat


class MessageIntegrityError(DecoderError):
    def __init__(self, calchash, urlhash, msg=None):
        if msg is None:
            # Set a default error message
            msg = "Checksum mismatch. Calculated hash = {}, URL hash = {}".format(calchash, urlhash)
        super().__init__(msg)
        self.calchash = calchash
        self.urlhash = urlhash


class NoCircularBufferError(DecoderError):
    def __init__(self, status, msg=None):
        if msg is None:
            # Set a default error message
            msg = "There is no circular buffer. This is indicative of an error with the system running the encoder. " \
                  "Status = {}".format(status)
        super().__init__(msg)
        self.status = status


class DelimiterNotFoundError(DecoderError):
    def __init__(self, circb64, status, msg=None):
        if msg is None:
            msg = " No delimiting character found in the circular buffer string = {}. The firmware has initialised " \
                  "the encoder but not pushed data. Status = {}".format(circb64, status)
        super().__init__(msg)
        self.circb64 = circb64
        self.status = status
