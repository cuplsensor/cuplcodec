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

        decsmpls = list()

        for pair in self.pairs:
            tempMsb = pair['tempMsb']
            rhMsb = pair['rhMsb']
            Lsb = pair['Lsb']

            tempLsb = (Lsb >> 4) & 0xF
            rhLsb = Lsb & 0xF
            temp = ((tempMsb << 4) | tempLsb)
            rh = ((rhMsb << 4) | rhLsb)

            temp = (temp * 165)/4096 - 40
            rh = (rh * 100)/4096

            decsmpl = {'temp':temp, 'rh':rh}
            decsmpls.append(decsmpl)

        self.smpls = self.applytimestamp(decsmpls, timeintminutes)
