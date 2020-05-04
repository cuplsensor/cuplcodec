import pytest
from wscodec.encoder.pyencoder.instrumented import InstrumentedSampleTRH
from wscodec.decoder import Decoder

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
    decodedurl = Decoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                         circb64=par['q'][0], ver=par['v'][0])

    assert encoder_cursorpos == decodedurl.params.buffer.endmarkerpos


@pytest.mark.parametrize('n', [1, 300])
def test_loopcount(instr_sample, n):
    instr_sample.pushsamples((instr_sample.ffimodule.lib.buflenpairs+ 4) * n + 1)

    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = Decoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                         circb64=par['q'][0], ver=par['v'][0])

    assert decodedurl.params.status.loopcount == n


@pytest.mark.parametrize('resetsalltime', [1, 300])
def test_resetsalltime(resetsalltime):
    instr_sample = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                         serial=INPUT_SERIAL,
                                         secretkey=INPUT_SECKEY,
                                         smplintervalmins=INPUT_TIMEINT,
                                         resetsalltime=resetsalltime)

    instr_sample.pushsamples(1)

    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = Decoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                         circb64=par['q'][0], ver=par['v'][0])

    assert decodedurl.params.status.resetsalltime == resetsalltime


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
    decodedurl = Decoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                         circb64=par['q'][0], ver=par['v'][0])

    assert decodedurl.params.status.get_batvoltageraw() == batteryadc
    assert decodedurl.params.status.get_resetcause() == resetcause
