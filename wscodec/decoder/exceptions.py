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

# Helpful: https://julien.danjou.info/python-exceptions-guide/

class DecoderError(Exception):
    """Base cupl Decoder error class."""

    def __init__(self, msg="cupl Decoder Error"):
        super().__init__(msg)


class InvalidMajorVersionError(DecoderError):
    def __init__(self, encoderversion, decoderversion, msg=None):
        if msg is None:
            # Set a default error messasge
            msg = "There is a mismatch between the encoder version = {} " \
                  "and decoder version = {} ".format(encoderversion, decoderversion)
        super().__init__(msg)
        self.encoderversion = encoderversion
        self.decoderversion = decoderversion


class InvalidFormatError(DecoderError):
    def __init__(self, circformat, msg=None):
        if msg is None:
            # Set a default error message
            msg = "Invalid circular buffer format = {}.".format(circformat)
        super().__init__(msg)
        self.circformat = circformat


class MessageIntegrityError(DecoderError):
    def __init__(self, calchash, urlhash, msg=None):
        if msg is None:
            # Set a default error message
            msg = "Checksum mismatch. Calculated hash = {}, URL hash = {}".format(calchash, urlhash)
        super().__init__(msg)
        self.calchash = calchash
        self.urlhash = urlhash


class NoCircularBufferError(DecoderError):
    def __init__(self, status, msg=None):
        if msg is None:
            # Set a default error message
            msg = "There is no circular buffer. This is indicative of an error with the system running the encoder. " \
                  "Status = {}".format(status)
        super().__init__(msg)
        self.status = status


class DelimiterNotFoundError(DecoderError):
    def __init__(self, circb64, status, msg=None):
        if msg is None:
            msg = " No delimiting character found in the circular buffer string = {}. The firmware has initialised " \
                  "the encoder but not pushed data. Status = {}".format(circb64, status)
        super().__init__(msg)
        self.circb64 = circb64
        self.status = status
