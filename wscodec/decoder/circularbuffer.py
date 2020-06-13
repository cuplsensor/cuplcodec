from wscodec.decoder.status import Status
from datetime import datetime
from .exceptions import InvalidCircFormatError
from .hdc2021 import HDC2021DecoderHT, HDC2021DecoderT


class CircularBufferDecoder:
    @staticmethod
    def decode(formatcode: int, timeintminutes: int, circbuf64: str, secretkey: str, status: Status, usehmac: bool, scandatetime: datetime):
        formats = {
            1: HDC2021DecoderHT,
            2: HDC2021DecoderT
        }
        try:
            decoded = formats[formatcode](timeintminutes, circbuf64, secretkey, status, usehmac, scandatetime)
        except KeyError:
            raise InvalidCircFormatError(formatcode)

        return decoded