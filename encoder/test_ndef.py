import pytest
from base64 import urlsafe_b64decode
from encoder.pyencoder.instrumented import InstrumentedNDEF
from urldecoder.urldecoder import UrlDecoder
from urllib.parse import urlparse

INPUT_SERIAL = 'abcdabcd'
INPUT_TIMEINT = 12
INPUT_SECKEY = 'AAAABBBB'
INPUT_STATUSB64 = 'MDAwMDAw'
INPUT_CBUFLENBLKS = 32

@pytest.fixture(scope="function",
                params=["plotsensor.com", "toastersrg.plotsensor.com"])
def instr_ndef(request):
    ndefobj = InstrumentedNDEF(baseurl=request.param, serial=INPUT_SERIAL, secretkey=INPUT_SECKEY, smplintervalmins=INPUT_TIMEINT)
    ndefobj.baseurl = request.param
    return ndefobj

@pytest.fixture
def makeblankurl(instr_ndef):
    ndefobj = instr_ndef
    cbuflenblks = INPUT_CBUFLENBLKS
    statusb64bytes = INPUT_STATUSB64.encode('ascii')
    statusb64chars = ndefobj.ffimodule.ffi.new("char[]", statusb64bytes)
    startblkptr = ndefobj.ffimodule.ffi.new("int *", 0)
    ndefobj.ffimodule.lib.ndef_writeblankurl(cbuflenblks, statusb64chars, startblkptr)
    return ndefobj

@pytest.fixture
def blankurlqs(makeblankurl):
    # Obtain the URL parameters dictionary from the Mock EEPROM
    return makeblankurl.eepromba.get_url_parsedqs()

@pytest.fixture
def blankurlraw(makeblankurl):
    # Obtain the URL parameters dictionary from the Mock EEPROM
    return makeblankurl.eepromba.get_message()


def test_calclen(instr_ndef):
    ndefobj = instr_ndef
    paddinglen = ndefobj.ffimodule.ffi.new("int *")
    preamblenbytes = ndefobj.ffimodule.ffi.new("int *")
    urllen = ndefobj.ffimodule.ffi.new("int *")
    paddinglen[0] = 0
    preamblenbytes[0] = 0
    urllen[0] = len(ndefobj.baseurl)
    ndefobj.ffimodule.lib.ndef_calclen(paddinglen, preamblenbytes, urllen)
    x = preamblenbytes[0]
    assert (x) % 16 == 0


def test_baseurl(makeblankurl):
    blankurl = makeblankurl.eepromba.get_url()
    baseurl = urlparse(blankurl).netloc
    assert baseurl == makeblankurl.baseurl


def test_serial(blankurlqs):
    serial = blankurlqs['s'][0]
    assert serial == INPUT_SERIAL


def test_timeinterval(blankurlqs):
    timeintb64 = blankurlqs['t'][0]
    timeintbytes = urlsafe_b64decode(timeintb64)
    timeint = int.from_bytes(timeintbytes, byteorder='little')
    assert timeint == INPUT_TIMEINT


def test_statusbytes(blankurlqs):
    statb64 = blankurlqs['x'][0]
    assert statb64 == INPUT_STATUSB64


def test_circbuf_length(blankurlqs):
    circb64 = blankurlqs['q'][0]
    blksizebytes = 16
    assert len(circb64) / blksizebytes == INPUT_CBUFLENBLKS


def test_decode_raises_indexerrror(blankurlqs):
    serial = blankurlqs['s'][0]
    timeintb64 = blankurlqs['t'][0]
    statb64 = blankurlqs['x'][0]
    circb64 = blankurlqs['q'][0]
    ver = blankurlqs['v'][0]
    with pytest.raises(IndexError):
        # Attempt to decode the parameters
        decoded = UrlDecoder(secretkey=INPUT_SECKEY,
                             timeintb64=timeintb64,
                             statb64=statb64,
                             circb64=circb64,
                             ver=ver)
