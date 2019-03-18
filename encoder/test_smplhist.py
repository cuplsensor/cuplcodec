import pytest
from encoder.pyencoder.instrumented import InstrumentedSmplHist
import random
import hmac
import hashlib

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAABBBBCCCCDDDD'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32

PADDING = 2


@pytest.fixture(scope="function",
                params=[{'baseurl': "plotsensor.com", 'secretkey': "AAAACCCCDDDDEEEE"},
                        {'baseurl': "toastersrg.plotsensor.com", 'secretkey': "AAAABBBBCCCCDEDE"},
                        {'baseurl': "plotsensor.com", 'secretkey': "masf349212345678"},
                        {'baseurl': "plotsensor.com", 'secretkey': "42r3223355778899"}
                        ])
def instr_smplhist(request):
    return InstrumentedSmplHist(baseurl=request.param['baseurl'],
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
        sensordata = instr.ffimodule.ffi.new("sdchars_t *", {'m1Msb': m1Msb, 'm2Msb': m2Msb, 'Lsb': Lsb})
        sdbytearray = bytearray([m1Msb, m2Msb, Lsb]) + sdbytearray
        sdlist.insert(0, sensordata[0])
        instr.ffimodule.lib.smplhist_push(sensordata[0])
    return sdlist, sdbytearray


def check_buffer(instr, sdlist):
    bufindex = 0
    errorflag = instr.ffimodule.ffi.new("int *", 0)
    for sensordata in sdlist:
        bufsd = instr.ffimodule.lib.smplhist_read(bufindex, errorflag)
        bufindex = bufindex + 1
        assert bufsd.m1Msb == sensordata.m1Msb and bufsd.m2Msb == sensordata.m2Msb and bufsd.Lsb == sensordata.Lsb


@pytest.fixture(scope="function", params=[1, 10, 100, -1])
def instr_smplhist_with_samples(instr_smplhist, request):
    if request.param is -1:
        nsamples = instr_smplhist.ffimodule.lib.buflensamples
    else:
        nsamples = request.param
    sdlist, sdba = write_buffer(instr_smplhist, n=nsamples)
    return {'instr_smplhist': instr_smplhist, 'sdlist': sdlist, 'sdba': sdba, 'nsamples': nsamples}


def get_uut_digest(instr_smplhist_with_samples, hmac=False):
    instr_smplhist = instr_smplhist_with_samples['instr_smplhist']
    nsamples = instr_smplhist_with_samples['nsamples']

    uutdigest = instr_smplhist.ffimodule.lib.smplhist_md5(nsamples, hmac).md5
    lendigest = len(uutdigest)

    uutdigeststr = ""
    for i in range(0, lendigest):
        # https://stackoverflow.com/questions/12638408/decorating-hex-function-to-pad-zeros
        uutdigeststr += f"{uutdigest[i]:0{PADDING}x}"

    return uutdigeststr


def test_buffer_load(instr_smplhist_with_samples):
    check_buffer(instr_smplhist_with_samples['instr_smplhist'], instr_smplhist_with_samples['sdlist'])


def test_hmac(instr_smplhist_with_samples):
    secretkey = instr_smplhist_with_samples['instr_smplhist'].secretkey
    secretkeyba = bytearray(secretkey.encode('utf-8'))

    uutdigest = get_uut_digest(instr_smplhist_with_samples, hmac=True)
    sdba = instr_smplhist_with_samples['sdba']

    hmacobj = hmac.new(secretkeyba, sdba, 'md5')
    tbdigest = hmacobj.hexdigest()
    tbdigest = tbdigest[0:len(uutdigest)]

    assert tbdigest == uutdigest


def test_hmac_fail(instr_smplhist_with_samples):
    secretkey = bytes(b"12345678")

    uutdigest = get_uut_digest(instr_smplhist_with_samples, hmac=True)
    sdba = instr_smplhist_with_samples['sdba']

    hmacobj = hmac.new(secretkey, sdba, 'md5')
    tbdigest = hmacobj.hexdigest()
    tbdigest = tbdigest[0:len(uutdigest)]

    assert tbdigest != uutdigest


def test_md5(instr_smplhist_with_samples):
    uutdigest = get_uut_digest(instr_smplhist_with_samples, hmac=False)
    sdba = instr_smplhist_with_samples['sdba']

    m = hashlib.md5()
    m.update(sdba)
    tbdigest = m.hexdigest()
    tbdigest = tbdigest[0:len(uutdigest)]

    assert tbdigest == uutdigest



