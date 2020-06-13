from wscodec.decoder.status import Status
from datetime import datetime
from .exceptions import InvalidCircFormatError
from .htdecoder import HTBufferDecoder
from .tdecoder import TBufferDecoder


class CircularBufferDecoder:
    @staticmethod
    def decode(formatcode: int, timeintminutes: int, circbuf64: str, secretkey: str, status: Status, usehmac: bool, scandatetime: datetime):
        formats = {
            1: HTBufferDecoder,
            2: TBufferDecoder
        }
        try:
            decoded = formats[formatcode](timeintminutes, circbuf64, secretkey, status, usehmac, scandatetime)
        except KeyError:
            raise InvalidCircFormatError(formatcode)

        return decoded