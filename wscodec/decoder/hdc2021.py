from .pairsdecoder import PairsDecoder
from wscodec.decoder.status import Status
from datetime import datetime


class HDC2021Decoder(PairsDecoder):
    @staticmethod
    def reading_to_temp(reading):
        return (reading * 165)/4096 - 40

    @staticmethod
    def reading_to_rh(reading):
        return (reading * 100)/4096


class HTDecoder(HDC2021Decoder):
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

            temp = HDC2021Decoder.reading_to_temp(temp)
            rh = HDC2021Decoder.reading_to_rh(rh)

            samples.append({'temp': temp, 'rh': rh})

        self.samples = self.applytimestamp(samples, timeintminutes)


class TDecoder(HDC2021Decoder):
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
                temp2 = HDC2021Decoder.reading_to_temp(pair.rd1)
                samples.append({'temp': temp2})

            temp1 = HDC2021Decoder.reading_to_temp(pair.rd0)
            samples.append({'temp': temp1})

        self.samples = self.applytimestamp(samples, timeintminutes)
