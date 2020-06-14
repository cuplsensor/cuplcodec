from datetime import timezone, datetime
from .b64decode import b64decode
from .status import Status


class ParamDecoder:
    def __init__(self, statb64: str, timeintb64: str, circb64: str, usehmac: bool = False, secretkey: str = None, scandatetime: datetime = None):
        self.statb64 = statb64
        self.timeintb64 = timeintb64
        self.circb64 = circb64
        self.usehmac = usehmac
        self.secretkey = secretkey
        self.scandatetime = scandatetime or datetime.now(timezone.utc)

    def decode(self):
        self.decode_timeinterval()
        self.status = Status(self.statb64)

    def decode_timeinterval(self):
        """
        Calculates the time interval in minutes from a URL parameter.
        """

        timeintbytes = b64decode(self.timeintb64)
        self.timeintervalmins = int.from_bytes(timeintbytes, byteorder='little')