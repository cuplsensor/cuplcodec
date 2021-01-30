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
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAABBBBCCCCDDDD'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32
INPUT_BASEURL = "plotsensor.com"

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': INPUT_BASEURL, 'secretkey': INPUT_SECKEY}
                        ])
def instr_sample(request):
    return InstrumentedSampleTRH(baseurl=request.param['baseurl'],
                                 serial=INPUT_SERIAL,
                                 secretkey=request.param['secretkey'],
                                 smplintervalmins=INPUT_TIMEINT)


def test_status(instr_sample, n=1):
    instr_sample.pushsamples(n)
    encoder_cursorpos = instr_sample.ffimodule.lib.demi_getendmarkerpos()

    # Decode the URL
    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0])

    assert encoder_cursorpos == decodedurl.endmarkerpos


@pytest.mark.parametrize('n', [1, 300])
def test_loopcount(instr_sample, n):
    instr_sample.pushsamples((instr_sample.ffimodule.lib.buflenpairs + 4) * n + 1)

    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0])

    assert decodedurl.status.loopcount == n


@pytest.mark.parametrize('resetsalltime', [1, 300])
def test_resetsalltime(resetsalltime):
    instr_sample = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                         serial=INPUT_SERIAL,
                                         secretkey=INPUT_SECKEY,
                                         smplintervalmins=INPUT_TIMEINT,
                                         resetsalltime=resetsalltime)

    instr_sample.pushsamples(1)

    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0])

    assert decodedurl.status.resetsalltime == resetsalltime


@pytest.mark.parametrize('resetcause', [1, 100, 254])
@pytest.mark.parametrize('batteryadc', [1, 100, 254])
def test_batteryvoltage(resetcause, batteryadc):
    instr_sample = InstrumentedSampleTRH(batteryadc=batteryadc)
    # Hack. Sorry. The def_extern must be defined beforehand but this is not possible if instr_sample does not exist.
    # Any better way of doing this please PR.

    instr_sample = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                         serial=INPUT_SERIAL,
                                         secretkey=INPUT_SECKEY,
                                         smplintervalmins=INPUT_TIMEINT,
                                         batteryadc=batteryadc,
                                         resetcause=resetcause)

    instr_sample.pushsamples(2)

    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0])

    assert decodedurl.status.get_batvoltageraw() == batteryadc
    assert decodedurl.status.get_resetcauseraw() == resetcause
