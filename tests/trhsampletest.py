from .sampletest import *

class TRHSampleTest(SampleTest):
    def setUp(self):
        super(TRHSampleTest, self).setUp(secretkey='AAAACCCC')

    def test_one(self):
        inlist = self.pushsamples(100)
        urllist = self.geturllist()
        inlist = inlist[:len(urllist)]
        self.comparelists(urllist, inlist)

class TSampleTest(SampleTest):
    def setUp(self):
        super(TSampleTest, self).setUp(secretkey='AAAACCCC')

    def test_one(self):
        inlist = self.pushsamples(100)
        urllist = self.geturllist()
        inlist = inlist[:len(urllist)]
        self.comparelists(urllist, inlist)

if __name__ == "__main__":
    unittest.main()
