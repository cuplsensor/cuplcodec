from .pairsdecoder import PairsDecoder
from wscodec.decoder.status import Status
from datetime import datetime


class HTBufferDecoder(PairsDecoder):
    """
    Extracts samples containing 2 measurands (temperature and humidity) from the circular buffer.

    Parameters
    ----------
    timeintminutes : int
        Time interval between samples in minutes.

    circbuf64 : str
        Circular buffer string containing samples encoded in base64.

    secretkey : str
        Secret key used to verify the source of the samples.

    """
    def __init__(self, timeintminutes: int, circbuf64: str, secretkey: str, status: Status, usehmac: bool, scandatetime: datetime):
        super().__init__(circbuf64, secretkey, status, usehmac, scandatetime)

        samples = list()

        for pair in self.pairs:
            temp = pair.rd0
            rh = pair.rd1

            temp = (temp * 165)/4096 - 40
            rh = (rh * 100)/4096

            samples.append({'temp': temp, 'rh': rh})

        self.samples = self.applytimestamp(samples, timeintminutes)
