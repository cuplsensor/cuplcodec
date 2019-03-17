import pytest
from encoder.pyencoder.instrumented import InstrumentedSampleTRH
from decoder import UrlDecoder

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAACCCC'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': "plotsensor.com", 'secretkey': "AAAACCCC"}
                        ])
def instr_sample(request):
    return InstrumentedSampleTRH(baseurl=request.param['baseurl'],
                              serial=INPUT_SERIAL,
                              secretkey=request.param['secretkey'],
                              smplintervalmins=INPUT_TIMEINT)


@pytest.mark.parametrize('n', range(1, 260))
def test_cursorpos(instr_sample, n):
    instr_sample.pushsamples(n)
    x = instr_sample.ffimodule.lib.octet_getcursorpos()

    # Decode the URL
    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = UrlDecoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], ver=par['v'][0])

    assert (decodedurl.decoded.cursorpos >> 2) + 4 == x
