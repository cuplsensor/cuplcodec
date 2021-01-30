#  cuplcodec encodes environmental sensor data into a URL and the reverse.
#
#  https://github.com/cuplsensor/cuplcodec
#
#  Original Author: Malcolm Mackay
#  Email: malcolm@plotsensor.com
#  Website: https://cupl.co.uk
#
#  Copyright (C) 2021. Plotsensor Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from datetime import datetime
from .samples import SamplesURL, Sample


class TempSample(Sample):
    def __init__(self, rawtemp: int, timestamp: datetime):
        """

        :param rawtemp:
        :param timestamp:
        """
        super().__init__(timestamp)
        self.rawtemp = rawtemp
        self.temp = self.reading_to_temp(rawtemp)

    @staticmethod
    def reading_to_temp(reading: int) -> float:
        """
        :param reading: Integer temperature ADC reading from the HDC2021.
        :return: Temperature in degrees C
        """
        return (reading * 165) / 4096 - 40


class TempRHSample(TempSample):
    def __init__(self, rawtemp: int, rawrh: int, timestamp: datetime):
        super().__init__(rawtemp, timestamp)
        self.rawrh = rawrh
        self.rh = self.reading_to_rh(rawrh)

    @staticmethod
    def reading_to_rh(reading: int) -> float:
        """

        :param reading: Integer Relative Humidity ADC reading from the HDC2021.
        :return: Relative Humidity in percent.
        """
        return (reading * 100) / 4096


class TempRH_URL(SamplesURL):
    def __init__(self, *args, **kwargs):
        """
        :return: Decoded URL parameters with buffer data converted to a list of timestamped samples, each containing
        temperature (degrees C) and relative humidity (%) readings.
        """
        super().__init__(*args, **kwargs)
        timestamp_gen = self.generate_timestamp()

        for pair in self.pairs:
            temp = pair.rd0
            rh = pair.rd1

            sample = TempRHSample(temp, rh, timestamp=next(timestamp_gen))
            self.samples.append(sample)


class Temp_URL(SamplesURL):
    def __init__(self, *args, **kwargs):
        """

        :return: Decoded URL parameters with buffer data converted to a list of timestamped samples, each containing one
        temperature reading in degrees C.
        """
        super().__init__(*args, **kwargs)
        timestamp_gen = self.generate_timestamp()

        for pair in self.pairs:
            if pair.rd1 != 4095:
                sample = TempSample(pair.rd1, timestamp=next(timestamp_gen))
                self.samples.append(sample)

            sample = TempSample(pair.rd0, timestamp=next(timestamp_gen))
            self.samples.append(sample)
