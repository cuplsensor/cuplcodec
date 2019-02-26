import unitc
import unittest
from struct import *
import hashlib
import hmac

class HistTest(unittest.TestCase):
    def setUp(self):
        self.module, self.ffi, self.filename = unitc.load('smplhist', ['md5'])
        super(HistTest, self).setUp()

    def test_one_sample(self):
        sdlist, sdba = self.populate_buffer(n=10)
        self.check_buffer(sdlist)

    def test_full_samples(self):
        nsamples = self.module.buflensamples-1
        self.populate_buffer(n=100)
        sdlist, sdba = self.populate_buffer(n=nsamples)
        self.check_buffer(sdlist)

    def populate_buffer(self, n):
        sdlist = list()
        sdbytearray = bytearray()
        for i in range(0, n):
            bufbyte = i.to_bytes(1, 'little')
            sensordata = self.ffi.new("sd_t *", {'temp': bufbyte, 'rh': bufbyte})
            sdbytearray = bytearray(bufbyte) + sdbytearray
            sdbytearray = bytearray(bufbyte) + sdbytearray
            sdlist.insert(0, sensordata[0])
            self.module.smplhist_push(sensordata[0])
        #sdbytearray = sdbytearray.reverse()
        return sdlist, sdbytearray

    def check_buffer(self, sdlist):
        bufindex = 0
        for sensordata in sdlist:
            bufsd = self.module.smplhist_read(bufindex)
            bufindex = bufindex + 1
            #print("temp={} rh={}".format(sensordata.temp, sensordata.rh))
            #print("temp={} rh={}".format(bufsd.temp, bufsd.rh))
            self.assertEqual(bufsd.temp, sensordata.temp)
            self.assertEqual(bufsd.rh, sensordata.rh)

    def test_md5(self):
        nsamples = self.module.buflensamples-1
        self.populate_buffer(n=2)
        sdlist, sdba = self.populate_buffer(n=nsamples)
        m = hashlib.md5()
        m.update(sdba)
        uutmd5 = self.module.smplhist_md5(nsamples, False).md5
        lenmd5 = len(uutmd5)
        tbmd5 = m.hexdigest()[0:2*lenmd5]
        uutmd5hexstr = ""
        padding = 2
        for i in range(0, lenmd5):
            # https://stackoverflow.com/questions/12638408/decorating-hex-function-to-pad-zeros
            uutmd5hexstr += f"{uutmd5[i]:0{padding}x}"
        self.assertEqual(tbmd5, uutmd5hexstr, msg=nsamples)

    def test_hmac(self):
        secretkey = bytearray(b"AAAACCCC")
        nsamples = self.module.buflensamples - 1
        sdlist, sdba = self.populate_buffer(n=nsamples)
        hmacobj = hmac.new(secretkey, sdba)
        tbdigest = hmacobj.hexdigest()
        uutdigest = self.module.smplhist_md5(nsamples, True).md5
        lendigest = len(uutdigest)
        tbdigest = tbdigest[0:2*lendigest]
        padding = 2
        uutdigeststr = ""
        for i in range(0, lendigest):
            # https://stackoverflow.com/questions/12638408/decorating-hex-function-to-pad-zeros
            uutdigeststr += f"{uutdigest[i]:0{padding}x}"
        self.assertEqual(tbdigest, uutdigeststr)

    def tearDown(self):
        # Delete file
        unitc.teardown(self.filename)

if __name__ == "__main__":
    unittest.main()
