import pytest
from wscodec.encoder.pyencoder.instrumented import InstrumentedPairhist
import random
import hmac
import hashlib

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAABBBBCCCCDDDD'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32

PADDING = 2
# This is for loopcount, resetsalltime, batv_resetcause and endmarkerpos.
# Not part of the test so are set to zero.
LOOPCOUNT = 0
RESETSALLTIME = 0
BATV_RESETCAUSE = 0
ENDMARKERPOS = 0
ZERO_STAT_AND_ENDMARKERPOS = bytearray(8)


@pytest.fixture(scope="function",
                params=[{'baseurl': "plotsensor.com", 'secretkey': "AAAACCCCDDDDEEEE"},
                        {'baseurl': "toastersrg.plotsensor.com", 'secretkey': "AAAABBBBCCCCDEDE"},
                        {'baseurl': "plotsensor.com", 'secretkey': "masf349212345678"},
                        {'baseurl': "plotsensor.com", 'secretkey': "42r3223355778899"}
                        ])
def instr_pairhist(request):
    return InstrumentedPairhist(baseurl=request.param['baseurl'],
                                serial=INPUT_SERIAL,
                                secretkey=request.param['secretkey'],
                                smplintervalmins=INPUT_TIMEINT)

def convertToSdChars(meas1, meas2):
    m1Msb = (meas1 >> 4)
    m2Msb = (meas2 >> 4)
    Lsb = (((meas1 & 0xF) << 4) & (meas2 & 0xF))
    return m1Msb, m2Msb, Lsb


def write_buffer(instr, n):
    sdlist = list()
    sdbytearray = bytearray()
    for i in range(0, n):
        testsample = random.randrange(4095)
        m1Msb, m2Msb, Lsb = convertToSdChars(testsample, testsample)
        sensordata = instr.ffimodule.ffi.new("pair_t *", {'m1Msb': m1Msb, 'm2Msb': m2Msb, 'Lsb': Lsb})
        sdbytearray = bytearray([m1Msb, m2Msb, Lsb]) + sdbytearray
        sdlist.insert(0, sensordata[0])
        instr.ffimodule.lib.pairhist_push(sensordata[0])
    return sdlist, sdbytearray


def check_buffer(instr, sdlist):
    bufindex = 0
    errorflag = instr.ffimodule.ffi.new("int *", 0)
    for sensordata in sdlist:
        bufsd = instr.ffimodule.lib.pairhist_read(bufindex, errorflag)
        bufindex = bufindex + 1
        assert bufsd.m1Msb == sensordata.m1Msb and bufsd.m2Msb == sensordata.m2Msb and bufsd.Lsb == sensordata.Lsb


@pytest.fixture(scope="function", params=[1, 10, 100, -1])
def instr_pairhist_with_samples(instr_pairhist, request):
    if request.param is -1:
        nsamples = instr_pairhist.ffimodule.lib.buflenpairs
    else:
        nsamples = request.param
    sdlist, sdba = write_buffer(instr_pairhist, n=nsamples)
    return {'instr_pairhist': instr_pairhist, 'sdlist': sdlist, 'sdba': sdba, 'nsamples': nsamples}


def get_uut_digest(instr_pairhist_with_samples, hmac=False):
    instr_pairhist = instr_pairhist_with_samples['instr_pairhist']
    nsamples = instr_pairhist_with_samples['nsamples']

    uutdigest = instr_pairhist.ffimodule.lib.pairhist_md5(nsamples,
                                                          hmac,
                                                          LOOPCOUNT,
                                                          RESETSALLTIME,
                                                          BATV_RESETCAUSE,
                                                          ENDMARKERPOS).md5
    lendigest = len(uutdigest)

    uutdigeststr = ""
    for i in range(0, lendigest):
        # https://stackoverflow.com/questions/12638408/decorating-hex-function-to-pad-zeros
        uutdigeststr += f"{uutdigest[i]:0{PADDING}x}"

    return uutdigeststr


def test_buffer_load(instr_pairhist_with_samples):
    check_buffer(instr_pairhist_with_samples['instr_pairhist'], instr_pairhist_with_samples['sdlist'])


def test_hmac(instr_pairhist_with_samples):
    secretkey = instr_pairhist_with_samples['instr_pairhist'].secretkey
    secretkeyba = bytearray(secretkey.encode('utf-8'))

    uutdigest = get_uut_digest(instr_pairhist_with_samples, hmac=True)
    sdba = instr_pairhist_with_samples['sdba'] + ZERO_STAT_AND_ENDMARKERPOS

    hmacobj = hmac.new(secretkeyba, sdba, 'md5')
    tbdigest = hmacobj.hexdigest()
    tbdigest = tbdigest[0:len(uutdigest)]

    assert tbdigest == uutdigest


def test_hmac_fail(instr_pairhist_with_samples):
    secretkey = bytes(b"12345678")

    uutdigest = get_uut_digest(instr_pairhist_with_samples, hmac=True)
    sdba = instr_pairhist_with_samples['sdba']

    hmacobj = hmac.new(secretkey, sdba, 'md5')
    tbdigest = hmacobj.hexdigest()
    tbdigest = tbdigest[0:len(uutdigest)]

    assert tbdigest != uutdigest


def test_md5(instr_pairhist_with_samples):
    uutdigest = get_uut_digest(instr_pairhist_with_samples, hmac=False)
    sdba = instr_pairhist_with_samples['sdba']

    m = hashlib.md5()
    m.update(sdba)
    m.update(ZERO_STAT_AND_ENDMARKERPOS) # PAD WITH 8 ZEROES
    tbdigest = m.hexdigest()
    tbdigest = tbdigest[0:len(uutdigest)]

    assert tbdigest == uutdigest



