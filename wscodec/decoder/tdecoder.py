from .pairsdecoder import PairsDecoder
from wscodec.decoder.status import Status
from datetime import datetime


class TBufferDecoder(PairsDecoder):
    """
    Extracts temperature samples from the circular buffer.

    Parameters
    ----------
    circbuf64 : str
        Circular buffer string containing temperature samples encoded in base64.

    timeintminutes : int
        Time interval between samples in minutes.

    secretkey : str
        Secret key used to verify the source of the samples.

    """
    def __init__(self, timeintminutes: int, circbuf64: str, secretkey: str, status: Status, usehmac: bool, scandatetime: datetime):
        super().__init__(circbuf64, secretkey, status, usehmac, scandatetime)

        samples = list()

        for pair in self.pairs:
            if pair.rd1 != 4095:
                temp2 = (pair.rd1 * 165)/4096 - 40
                samples.append({'temp': temp2})

            temp1 = (pair.rd0 * 165)/4096 - 40
            samples.append({'temp': temp1})

        self.samples = self.applytimestamp(samples, timeintminutes)
