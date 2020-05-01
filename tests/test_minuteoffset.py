import pytest
from wscodec.encoder.pyencoder.instrumented import InstrumentedSampleTRH
from wscodec.decoder import Decoder

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
        instr_sample.ffimodule.lib.cbuf_setelapsed(i)

        # Decode the URL
        par = instr_sample.eepromba.get_url_parsedqs()
        decodedurl = Decoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                             circb64=par['q'][0], ver=par['v'][0])

        assert i == decodedurl.params.buffer.minuteoffset



