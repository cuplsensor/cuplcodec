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
from wscodec.encoder.pyencoder.instrumented import InstrumentedSampleTRH, InstrumentedSample
from wscodec.decoder import decode
from wscodec.decoder.exceptions import NoCircularBufferError, DelimiterNotFoundError, InvalidMajorVersionError, \
    InvalidFormatError, MessageIntegrityError
from wscodec.decoder.status import SVSH_BIT

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAABBBBCCCCDDDD'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32
INPUT_BASEURL = "plotsensor.com"

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': "plotsensor.com", 'secretkey': "AAAABBBBCCCCDDDE"},
                        {'baseurl': "toastersrg.plotsensor.com", 'secretkey': "AAAABBBBCCCCDDDF"},
                        {'baseurl': "plotsensor.com", 'secretkey': "AAAABBBBCCCCDDDG"},
                        {'baseurl': "plotsensor.com", 'secretkey': "AAAABBBBCCCCDDDX"}
                        ])
def instr_sample(request):
    return InstrumentedSampleTRH(baseurl=request.param['baseurl'],
                                 serial=INPUT_SERIAL,
                                 secretkey=request.param['secretkey'],
                                 smplintervalmins=INPUT_TIMEINT)


def comparelists(urllist, inlist):
    ONEBIT_ACCURACY = 165 / 4095
    assert len(urllist) == len(inlist)
    for x in range(0, 1, len(inlist)):
        for k, v in inlist[x].items():
            assert inlist[x][k] == pytest.approx(urllist[x][k], abs=ONEBIT_ACCURACY)


def test_lists_equal(instr_sample_populated):
    inlist = instr_sample_populated['inlist']
    urllist = instr_sample_populated['urllist']

    comparelists(urllist, inlist)


@pytest.mark.parametrize('n', range(1, 500, 1))
@pytest.mark.parametrize('usehmac', (True, False))
def test_md5(n, usehmac):
    instr_md5 = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                      serial=INPUT_SERIAL,
                                      secretkey=INPUT_SECKEY,
                                      smplintervalmins=INPUT_TIMEINT,
                                      usehmac=usehmac
                                      )

    inlist = instr_md5.pushsamples(n)

    # Decode the URL
    par = instr_md5.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey=INPUT_SECKEY, statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0], usehmac=usehmac)

    urllist = decodedurl.get_samples_list()
    for d in urllist:
        del d['timestamp']
        del d['rawtemp']
        del d['rawrh']

    inlist = inlist[:len(urllist)]

    comparelists(urllist, inlist)


def test_batteryvoltage():
    testbatv = 8

    instr_batv = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                       serial=INPUT_SERIAL,
                                       secretkey="",
                                       smplintervalmins=INPUT_TIMEINT,
                                       usehmac=False,
                                       batteryadc=testbatv)

    instr_batv.pushsamples(3)

    # Decode the URL
    par = instr_batv.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey="", statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0], usehmac=False)

    assert decodedurl.status.get_batvoltageraw() == testbatv


def test_error_nocircularbuffer():
    instr = InstrumentedSample(baseurl=INPUT_BASEURL,
                               serial=INPUT_SERIAL,
                               secretkey="",
                               smplintervalmins=INPUT_TIMEINT,
                               usehmac=False,
                               )

    resetcause = SVSH_BIT
    instr.ffimodule.lib.enc_init(resetcause, True, 0)

    par = instr.eepromba.get_url_parsedqs()

    with pytest.raises(NoCircularBufferError) as excinfo:
        # Attempt to decode the parameters
        decodedurl = decode(secretkey="", statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64="", vfmtb64=par['v'][0], usehmac=False)

    assert excinfo.value.status.resetcause['supervisor'] == True


def test_error_delimiternotfound():
    SECRETKEY = "12345678ABCDEFGH"
    instr = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                  serial=INPUT_SERIAL,
                                  secretkey=SECRETKEY,
                                  smplintervalmins=INPUT_TIMEINT,
                                  usehmac=True,
                                  )

    instr.ffimodule.lib.enc_init(0, False, 0)

    par = instr.eepromba.get_url_parsedqs()

    with pytest.raises(DelimiterNotFoundError) as excinfo:
        # Attempt to decode the parameters
        decodedurl = decode(secretkey=SECRETKEY, statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], vfmtb64=par['v'][0], usehmac=True)


def test_error_versionmismatch(mocker):
    instr = InstrumentedSample(baseurl=INPUT_BASEURL,
                               serial=INPUT_SERIAL,
                               secretkey="",
                               smplintervalmins=INPUT_TIMEINT,
                               usehmac=False,
                               )

    BAD_VERSION = 65500

    def mock_version():
        return BAD_VERSION

    instr.ffimodule.lib.enc_init(0, False, 0)

    par = instr.eepromba.get_url_parsedqs()

    mocker.patch('wscodec.decoder.decoderfactory._get_decoderversion', mock_version)

    with pytest.raises(InvalidMajorVersionError) as excinfo:
        # Attempt to decode the parameters
        decodedurl = decode(secretkey="", statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64="", vfmtb64=par['v'][0], usehmac=False)

    assert excinfo.value.decoderversion == BAD_VERSION


def test_error_formatmismatch():
    instr = InstrumentedSample(baseurl=INPUT_BASEURL,
                               serial=INPUT_SERIAL,
                               secretkey="",
                               smplintervalmins=INPUT_TIMEINT,
                               usehmac=False,
                               )

    BAD_FORMAT = 254
    instr.ffimodule.lib.nv.format = bytes([BAD_FORMAT])
    instr.ffimodule.lib.enc_init(0, False, 0)

    par = instr.eepromba.get_url_parsedqs()

    with pytest.raises(InvalidFormatError) as excinfo:
        # Attempt to decode the parameters
        decodedurl = decode(secretkey="", statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], vfmtb64=par['v'][0], usehmac=False)

    assert excinfo.value.circformat == BAD_FORMAT


def test_error_messageintegrity():
    instr = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                  serial=INPUT_SERIAL,
                                  secretkey="12345678ABCDEFGH",
                                  smplintervalmins=INPUT_TIMEINT,
                                  usehmac=True,
                                  )

    instr.ffimodule.lib.enc_init(0, False, 0)
    instr.pushsamples(100)

    par = instr.eepromba.get_url_parsedqs()

    with pytest.raises(MessageIntegrityError) as excinfo:
        # Attempt to decode the parameters
        decodedurl = decode(secretkey="notthekey", statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], vfmtb64=par['v'][0], usehmac=True)

def test_error_messageintegrity_wrongalgorithm():
    SECRETKEY = "12345678ABCDEFGH"
    instr = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                  serial=INPUT_SERIAL,
                                  secretkey=SECRETKEY,
                                  smplintervalmins=INPUT_TIMEINT,
                                  usehmac=True,
                                  )

    instr.ffimodule.lib.enc_init(0, False, 0)
    instr.pushsamples(100)

    par = instr.eepromba.get_url_parsedqs()

    with pytest.raises(MessageIntegrityError) as excinfo:
        # Attempt to decode the parameters
        decodedurl = decode(secretkey=SECRETKEY, statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], vfmtb64=par['v'][0], usehmac=False)