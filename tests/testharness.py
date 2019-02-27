import unittest
import weakref


class NDEFTest(unittest.TestCase):
    def setUp(self):
        self.global_weakkeydict = weakref.WeakKeyDictionary()

        super(NDEFTest, self).setUp()

    def test_blankurl(self):
        qlenblks = 32
        statusbytes = bytes(b"MDAwMDAw")
        statusb64 = self.ffi.new("char[]", statusbytes)
        startblkptr = self.ffi.new("int *", 0)
        retval = self.module.ndef_writeblankurl(qlenblks, statusb64, startblkptr, b'1')
        self.assertEqual(retval, 0)

class OctetBase:
    paddingoctet = "MDAwMDAw"

    def tpat(self, num,letter):
        strnum = str(num)
        strnum = strnum.rjust(4, '0')
        return strnum + letter*4

    def tpatbytes(self, num, letter):
        return bytes(self.tpat(num, letter), 'utf-8')

class TripleWriteSim(OctetBase):
    def __init__(self, qlenblks):
        self.qlenoctets = qlenblks * 2
        self.i = 0
        self.iteration = 1
        self.mylist = [self.paddingoctet] * self.qlenoctets

    def __iter__(self):
        return self

    def get_list(self):
        return self.mylist

    def next(self):
        i = self.i
        if self.i < self.qlenoctets-1:
            self.i += 1
        else:
            self.i = 0
        mystr = self.tpat(self.iteration, 'A')
        mystr2 = self.tpat(self.iteration, 'B')
        mystr3 = self.tpat(self.iteration, 'C')
        self.iteration += 1
        self.mylist[i] = mystr
        self.mylist[(i+1) % self.qlenoctets] = mystr2
        self.mylist[(i+2) % self.qlenoctets] = mystr3
        return self.i

class TripleWrite(OctetBase):
    def __init__(self, qlenblks, module, ffi):
        self.i = 1
        self.n = 9999
        self.module = module
        self.ffi = ffi
        statusbytes = bytes(self.paddingoctet, 'utf-8')
        statusb64 = self.ffi.new("char[]", statusbytes)
        startblkptr = self.ffi.new("int *", 0)
        retval = self.module.ndef_writeblankurl(qlenblks, statusb64, startblkptr, b'1')
        retval = self.module.octet_init(startblkptr[0], qlenblks)

    def __iter__(self):
        return self

    def next(self):
        if self.i < self.n:
            i = self.i
            self.i += 1
        else:
            i = self.i
            self.i = 1
        self.triple_write(i)
        return i

    def triple_write(self, iteration):
        testbytes1 = self.tpatbytes(iteration, 'A')
        testbytes2 = self.tpatbytes(iteration, 'B')
        testbytes3 = self.tpatbytes(iteration, 'C')
        retval = self.module.octet_write(self.module.Octet0, testbytes1)
        retval = self.module.octet_write(self.module.Octet1, testbytes2)
        retval = self.module.octet_write(self.module.Octet2, testbytes3)
        self.module.octet_commit4()
        self.module.octet_movecursor()

class OctetTest(EepromTest):
    def setUp(self):
        self.module, self.ffi, self.filename = unitc.load('octet', ['ndef','eep','base64'])
        super(OctetTest, self).setUp()

    def n_octets(self, qlenblks, iterations):
        tw = TripleWrite(qlenblks, self.module, self.ffi)
        twsim = TripleWriteSim(qlenblks)
        for i in range(0, iterations, 1):
            tw.next()
            twsim.next()
        qoctets = self.eepromba.get_qoctets()
        expqoctets = twsim.get_list()
        return expqoctets, qoctets

    def test_one_octet(self):
        iterations = 1
        qlenblks = 32
        expqoctets, qoctets = self.n_octets(qlenblks, iterations)
        self.assertEqual(len(qoctets), len(expqoctets))
        self.assertEqual(qoctets, expqoctets)

    def test_three_octets(self):
        iterations = 3
        qlenblks = 32
        expqoctets, qoctets = self.n_octets(qlenblks, iterations)
        self.assertEqual(len(qoctets), len(expqoctets))
        self.assertEqual(qoctets, expqoctets)

    def test_looparound_octets(self):
        iterations = 64
        qlenblks = 32
        expqoctets, qoctets = self.n_octets(qlenblks, iterations)
        self.assertEqual(len(qoctets), len(expqoctets))
        self.assertEqual(qoctets, expqoctets)

    def test_overwrite_octets(self):
        iterations = 70
        qlenblks = 50
        for iterations in range(1, 70, 1):
            expqoctets, qoctets = self.n_octets(qlenblks, iterations)
            self.assertEqual(len(qoctets), len(expqoctets))
            self.assertEqual(qoctets, expqoctets)



if __name__ == "__main__":
    unittest.main()
