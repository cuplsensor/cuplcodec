import pytest
from wscodec.encoder.pyencoder.instrumented import InstrumentedSampleTRH
from wscodec.decoder import decode

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAABBBBCCCCDDDD'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': "thehrhsdbsdrd.plotsensor.com", 'secretkey': INPUT_SECKEY},
                        {'baseurl': "plotsensor.com", 'secretkey': INPUT_SECKEY}
                        ])
def instr_sample(request):
    return InstrumentedSampleTRH(baseurl=request.param['baseurl'],
                              serial=INPUT_SERIAL,
                              secretkey=request.param['secretkey'],
                              smplintervalmins=INPUT_TIMEINT)


@pytest.mark.parametrize('n', range(1, 150))
def test_cursorpos(instr_sample, n):
    instr_sample.pushsamples(n)
    encoder_cursorpos = instr_sample.ffimodule.lib.demi_getendmarkerpos()

    # Decode the URL
    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                                       circb64=par['q'][0], ver=par['v'][0])

    assert encoder_cursorpos == decodedurl.endmarkerpos
