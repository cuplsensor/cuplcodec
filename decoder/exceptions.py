class DecoderError(Exception):
    """Base application error class."""

    def __init__(self):
        super().__init__()


class InvalidMajorVersionError(DecoderError):
    """ Raised when there is no decoder for the supplied major version.  """

    def __init__(self):
        super().__init__()
