from .pairsdecoder import PairsDecoder
from wscodec.decoder.status import Status
from datetime import datetime


class HDC2021Decoder(PairsDecoder):
    @staticmethod
    def reading_to_temp(reading: int) -> float:
        """

        :param reading: Integer temperature ADC reading from the HDC2021.
        :return: Temperature in degrees C
        """
        return (reading * 165)/4096 - 40

    @staticmethod
    def reading_to_rh(reading: int) -> float:
        """

        :param reading: Integer Relative Humidity ADC reading from the HDC2021.
        :return: Relative Humidity in percent.
        """
        return (reading * 100)/4096


class HDC2021DecoderHT(HDC2021Decoder):
    def decode(self):
        """
        :return: Decoded URL parameters with buffer data converted to a list of timestamped samples, each containing
        temperature (degrees C) and relative humidity (%) readings.
        """
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
    def decode(self):
        """

        :return: Decoded URL parameters with buffer data converted to a list of timestamped samples, each containing one
        temperature reading in degrees C.
        """
        super().decode()

        self.samples.clear()

        for pair in self.pairs:
            if pair.rd1 != 4095:
                temp2 = HDC2021Decoder.reading_to_temp(pair.rd1)
                self.samples.append({'temp': temp2})

            temp1 = HDC2021Decoder.reading_to_temp(pair.rd0)
            self.samples.append({'temp': temp1})

        self.applytimestamp()
