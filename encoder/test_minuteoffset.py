import pytest
from encoder.pyencoder.instrumented import InstrumentedSampleTRH
from decoder import UrlDecoder

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


def test_minuteoffset(instr_sample):
    instr_sample.pushsamples(1)

    for i in range(0, INPUT_TIMEINT, 5000):
        instr_sample.ffimodule.lib.sample_updateendstop(i)

        # Decode the URL
        par = instr_sample.eepromba.get_url_parsedqs()
        decodedurl = UrlDecoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], ver=par['v'][0])

        assert i == decodedurl.decoded.minuteoffset


