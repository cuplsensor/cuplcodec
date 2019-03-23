from .statdecoder import StatDecoder
from .htbufferdecoder import HTBufferDecoder
from .tbufferdecoder import TBufferDecoder
import base64


class ParamDecoder:
    """
        Description for class

        :ivar circformat: initial value: par1
        :ivar timeintervalmins: initial value: par2
        :ivar status: initial value: par2
        :ivar buffer: initial value: par2
        """

    def __init__(self, circformat, timeintb64, statb64, circb64, secretkey):
        if circformat == '1':
            bufferdecoder = HTBufferDecoder
        elif circformat == '2':
            bufferdecoder = TBufferDecoder
        else:
            raise ValueError()

        self.circformat = circformat
        self.timeintervalmins = ParamDecoder.decode_timeinterval(timeintb64)
        self.status = StatDecoder(statb64)
        self.buffer = bufferdecoder(circb64, self.timeintervalmins, secretkey)

    @staticmethod
    def decode_timeinterval(enctimeint):
        """
        Get the time interval in minutes from a URL parameter.

        Parameters
        -----------

        enctimeint
            Time interval in little endian byte order encoded as base64.

        Returns
        --------
        int
            Time interval in minutes

        """
        timeintbytes = base64.urlsafe_b64decode(enctimeint)
        timeint = int.from_bytes(timeintbytes, byteorder='little')
        return timeint
