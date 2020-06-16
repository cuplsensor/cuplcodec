from datetime import timezone, datetime
from .exceptions import DelimiterNotFoundError
from .b64decode import b64decode
from .status import Status

ENDSTOP_BYTE = '~'  # This must be URL Safe


class ParamDecoder:
    def __init__(self, statb64: str, timeintb64: str, circb64: str, usehmac: bool = False, secretkey: str = None, scandatetime: datetime = None):
        self.statb64 = statb64
        self.timeintb64 = timeintb64
        self.circb64 = circb64
        self.usehmac = usehmac
        self.secretkey = secretkey
        self.linearbuf = None
        self.scandatetime = scandatetime or datetime.now(timezone.utc)

    def decode(self):
        self._decode_timeinterval()
        self._linearise_buffer()
        self.status = Status(self.statb64)

    def _decode_timeinterval(self):
        """
        Calculates the time interval in minutes from a URL parameter.
        """

        timeintbytes = b64decode(self.timeintb64)
        self.timeintervalmins = int.from_bytes(timeintbytes, byteorder='little')

    def _linearise_buffer(self):
        """
        Linearise the circular buffer.
        """

        # Split query string at the end of the endstop marker.
        splitend = self.circb64.split(ENDSTOP_BYTE)

        if len(splitend) != 2:
            raise DelimiterNotFoundError(self.circb64, self.status)

        circbufstart = splitend[1]
        circbufend = splitend[0]

        self.endmarkerpos = len(circbufend)
        self.linearbuf = circbufstart + circbufend