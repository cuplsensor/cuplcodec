from .v1 import ParamDecoder as v1ParamDecoder
from .exceptions import InvalidMajorVersionError


class Decoder:
    """
    Construct a Decoder object

    :ivar majorversion: initial value: par2

    Parameters
    -----------
    secretkey
        Secret Key string.

    **reqargs
        A list of query string parameters

    """
    def __init__(self, secretkey, statb64, timeintb64, circb64, ver):
        majorversion = ver[-2:-1]
        circformat = ver[-1:]

        self.majorversion = majorversion

        if majorversion == '1':
            self.params = v1ParamDecoder(circformat, timeintb64, statb64, circb64, secretkey)
        else:
            raise InvalidMajorVersionError



