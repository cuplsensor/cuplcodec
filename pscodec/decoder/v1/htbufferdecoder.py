from .bufferdecoder import BufferDecoder


class HTBufferDecoder(BufferDecoder):
    """
    Extracts samples containing 2 measurands (temperature and humidity) from the circular buffer.

    Parameters
    ----------
    encstr : str
        Circular buffer string containing samples encoded in base64.

    timeintminutes : int
        Time interval between samples in minutes.

    secretkey : str
        Secret key used to verify the source of the samples.

    """
    def __init__(self, encstr, timeintminutes, secretkey, status, usehmac, scandatetime):
        super().__init__(encstr, secretkey, status, usehmac, scandatetime)

        decsmpls = list()

        for rawsmpl in self.rawsmpls:
            tempMsb = rawsmpl['tempMsb']
            rhMsb = rawsmpl['rhMsb']
            Lsb = rawsmpl['Lsb']

            tempLsb = (Lsb >> 4) & 0xF
            rhLsb = Lsb & 0xF
            temp = ((tempMsb << 4) | tempLsb)
            rh = ((rhMsb << 4) | rhLsb)

            temp = (temp * 165)/4096 - 40
            rh = (rh * 100)/4096

            decsmpl = {'temp':temp, 'rh':rh}
            decsmpls.append(decsmpl)

        self.smpls = self.applytimestamp(decsmpls, timeintminutes)
