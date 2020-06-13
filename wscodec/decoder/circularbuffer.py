from wscodec.decoder.status import Status
from datetime import datetime
from .exceptions import InvalidCircFormatError
from .hdc2021 import HTDecoder, TDecoder


class CircularBufferDecoder:
    @staticmethod
    def decode(formatcode: int, timeintminutes: int, circbuf64: str, secretkey: str, status: Status, usehmac: bool, scandatetime: datetime):
        formats = {
            1: HTDecoder,
            2: TDecoder
        }
        try:
            decoded = formats[formatcode](timeintminutes, circbuf64, secretkey, status, usehmac, scandatetime)
        except KeyError:
            raise InvalidCircFormatError(formatcode)

        return decoded