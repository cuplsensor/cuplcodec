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
                        circb64=par['q'][0], ver=par['v'][0], usehmac=False)

    urllist = decodedurl.get_samples_list()
    for d in urllist:
        del d['timestamp']
        del d['rawtemp']

    inlist = inlist[:len(urllist)]

    comparelists(urllist, inlist)
