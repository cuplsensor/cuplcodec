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

import base64


class B64Decoder:
    URLSAFE_PADDING_BYTE = '.'
    RFC3548_PADDING_BYTE = '='

    @classmethod
    def b64decode(cls, b64string):
        # Replace padding byte with RFC3548
        b64string = b64string.replace(cls.URLSAFE_PADDING_BYTE, cls.RFC3548_PADDING_BYTE)
        return base64.urlsafe_b64decode(b64string)