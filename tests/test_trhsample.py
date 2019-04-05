import pytest
from pscodec.encoder.pyencoder.instrumented import InstrumentedSampleTRH
from pscodec.decoder import Decoder

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


def test_md5():
    instr_md5 = InstrumentedSampleTRH(baseurl=INPUT_BASEURL,
                                  serial=INPUT_SERIAL,
                                  secretkey="",
                                  smplintervalmins=INPUT_TIMEINT,
                                  usehmac=False
                                  )

    inlist = instr_md5.pushsamples(500)

    # Decode the URL
    par = instr_md5.eepromba.get_url_parsedqs()
    decodedurl = Decoder(secretkey="", statb64=par['x'][0], timeintb64=par['t'][0],
                         circb64=par['q'][0], ver=par['v'][0], usehmac=False)

    urllist = decodedurl.params.buffer.smpls
    for d in urllist:
        del d['ts']

    inlist = inlist[:len(urllist)]

    comparelists(urllist, inlist)



