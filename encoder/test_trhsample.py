import pytest
from encoder.pyencoder.instrumented import InstrumentedSampleTRH

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAACCCC'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': "plotsensor.com", 'secretkey': "AAAACCCC"},
                        {'baseurl': "toastersrg.plotsensor.com", 'secretkey': "AAAABBBB"},
                        {'baseurl': "plotsensor.com", 'secretkey': "masf3492"},
                        {'baseurl': "plotsensor.com", 'secretkey': "42r32234"}
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



