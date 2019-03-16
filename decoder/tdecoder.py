from .decoder import Decoder
from datetime import datetime, timedelta

class TDecoder(Decoder):
    """
    Extracts temperature samples from the circular buffer.

    Parameters
    ----------
    encstr : str
        Circular buffer string containing temperature samples encoded in base64.

    timestamped : bool
        Indicates whether or not to timestamp the returned samples.

    timeintminutes : int
        Time interval between samples in minutes.

    secretkey : str
        Secret key used to verify the source of the samples.

    """
    def __init__(self, encstr, timestamped, timeintminutes, secretkey):
        super().__init__(encstr, secretkey)

        decsmpls = list()

        for rawsmpl in self.rawsmpls:
            tempMsb = rawsmpl['tempMsb']
            rhMsb = rawsmpl['rhMsb']
            Lsb = rawsmpl['Lsb']

            tempLsb = (Lsb >> 4) & 0xF
            rhLsb = Lsb & 0xF
            temp = ((tempMsb << 4) | tempLsb)
            rh = ((rhMsb << 4) | rhLsb)

            if rh != 4095:
                temp2 = (rh * 165)/4096 - 40
                decsmpls.append({'temp':temp2})

            temp1 = (temp * 165)/4096 - 40
            decsmpls.append({'temp':temp1})

        self.smpls = self.applytimestamp(decsmpls, timeintminutes)
