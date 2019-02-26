from testharness import *
import sys

sys.path.insert(0, '../../web/charityapp')

from urldecoder import UrlDecoder

class SampleTest(unittest.TestCase):
    def setUp(self, secretkey):
        self.secretkey = secretkey
        super(SampleTest, self).setUp()

    def getdecodedurl(self):
        par = self.eepromba.get_url_parsedqs()
        decodedurl = UrlDecoder(secretkey=self.secretkey, **par)
        return decodedurl

    def geturllist(self):
        par = self.eepromba.get_url_parsedqs()
        decodedurl = UrlDecoder(secretkey=self.secretkey, **par)
        urllist = decodedurl.decoded.smpls
        for d in urllist:
            del d['ts']
        return urllist

    def comparelists(self, urllist, inlist):
        self.assertEqual(len(urllist), len(inlist))
        for x in range(0, 1, len(inlist)):
            for k,v in inlist[x].items():
                self.assertAlmostEqual(urllist[x][k], inlist[x][k], delta=2)


if __name__ == "__main__":
    unittest.main()
