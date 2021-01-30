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
from wscodec.encoder.pyencoder.instrumented import InstrumentedSampleT
from wscodec.decoder import decode

INPUT_BASEURL = "cupl.uk"
INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAABBBBCCCCDDDD'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': "plotsensor.com", 'secretkey': INPUT_SECKEY}
                        ])
def instr_sample(request):
    return InstrumentedSampleT(baseurl=request.param['baseurl'],
                               serial=INPUT_SERIAL,
                               secretkey=request.param['secretkey'],
                               smplintervalmins=INPUT_TIMEINT)


def comparelists(urllist, inlist):
    ONEBIT_ACCURACY = 165 / 4096
    assert len(urllist) == len(inlist)
    for x in range(0, 1, len(inlist)):
        for k, v in inlist[x].items():
            assert inlist[x][k] == pytest.approx(urllist[x][k], abs=ONEBIT_ACCURACY)


def test_lists_equal(instr_sample_populated):
    inlist = instr_sample_populated['inlist']
    urllist = instr_sample_populated['urllist']

    comparelists(urllist, inlist)


@pytest.mark.parametrize('n', range(1, 500, 1))
def test_md5(instr_sample, n):
    instr_md5 = InstrumentedSampleT(baseurl=INPUT_BASEURL,
                                    serial=INPUT_SERIAL,
                                    secretkey="",
                                    smplintervalmins=INPUT_TIMEINT,
                                    usehmac=False
                                    )

    inlist = instr_md5.pushsamples(n)

    # Decode the URL
    par = instr_md5.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey="", statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0], usehmac=False)

    urllist = decodedurl.get_samples_list()
    for d in urllist:
        del d['timestamp']
        del d['rawtemp']

    inlist = inlist[:len(urllist)]

    comparelists(urllist, inlist)
