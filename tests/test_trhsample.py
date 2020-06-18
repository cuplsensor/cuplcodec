import pytest
from wscodec.encoder.pyencoder.instrumented import InstrumentedSampleTRH, InstrumentedSample
from wscodec.decoder import decode
from wscodec.decoder.exceptions import DelimiterNotFoundError
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
                        circb64=par['q'][0], ver=par['v'][0], usehmac=usehmac)

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
                        circb64=par['q'][0], ver=par['v'][0], usehmac=False)

    assert decodedurl.status.get_batvoltageraw() == testbatv


def test_errorcondition():
    instr = InstrumentedSample(baseurl=INPUT_BASEURL,
                               serial=INPUT_SERIAL,
                               secretkey="",
                               smplintervalmins=INPUT_TIMEINT,
                               usehmac=False,
                               )

    resetcause = SVSH_BIT
    instr.ffimodule.lib.enc_init(resetcause, True)

    par = instr.eepromba.get_url_parsedqs()

    with pytest.raises(DelimiterNotFoundError) as excinfo:
        # Attempt to decode the parameters
        decodedurl = decode(secretkey="", statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64="", ver=par['v'][0], usehmac=False)

    assert excinfo.value.status.resetcause['supervisor'] == True
