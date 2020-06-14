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


class HDC2021DecoderHT(HDC2021Decoder):
    """
    Extracts samples containing 2 measurands (temperature and humidity) from the circular buffer.
    """
    def decode(self):
        super().decode()

        self.samples.clear()

        for pair in self.pairs:
            temp = pair.rd0
            rh = pair.rd1

            temp = HDC2021Decoder.reading_to_temp(temp)
            rh = HDC2021Decoder.reading_to_rh(rh)

            self.samples.append({'temp': temp, 'rh': rh})

        self.applytimestamp()


class HDC2021DecoderT(HDC2021Decoder):
    """
    Extracts temperature samples from the circular buffer.

    """
    def decode(self):
        super().decode()

        self.samples.clear()

        for pair in self.pairs:
            if pair.rd1 != 4095:
                temp2 = HDC2021Decoder.reading_to_temp(pair.rd1)
                self.samples.append({'temp': temp2})

            temp1 = HDC2021Decoder.reading_to_temp(pair.rd0)
            self.samples.append({'temp': temp1})

        self.applytimestamp()
