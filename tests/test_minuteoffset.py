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

import pytest
from wscodec.encoder.pyencoder.instrumented import InstrumentedSampleTRH
from wscodec.decoder import decode

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 65535 # Maximum time interval
INPUT_SECKEY = 'AAAABBBBCCCCDDDD'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_BASEURL = 'plotsensor.com'
INPUT_CBUFLENBLKS = 32

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': "plotsensor.com", 'secretkey': INPUT_SECKEY}
                        ])
def instr_sample(request):
    return InstrumentedSampleTRH(baseurl=request.param['baseurl'],
                              serial=INPUT_SERIAL,
                              secretkey=request.param['secretkey'],
                              smplintervalmins=INPUT_TIMEINT)


def test_elapsedmins(instr_sample):
    instr_sample.pushsamples(1)

    for i in range(0, INPUT_TIMEINT, 5000):
        instr_sample.ffimodule.lib.enc_setelapsed(i)

        # Decode the URL
        par = instr_sample.eepromba.get_url_parsedqs()
        decodedurl = decode(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], vfmtb64=par['v'][0])

        assert i == decodedurl.elapsedmins



