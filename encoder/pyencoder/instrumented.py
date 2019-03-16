from .sharedobj import ndefpy, octetpy, smplhistpy, samplepy
from . import eeprom as eeprom
from struct import pack


class InstrumentedBase(object):
    """
    Put some documentation here
    """

    def __init__(self,
                 ffimodule,
                 baseurl,
                 serial,
                 secretkey,
                 smplintervalmins):
        self.secretkey = secretkey
        self.ffimodule = ffimodule
        self.ffimodule.lib.nv.serial = serial.encode('ascii')
        self.ffimodule.lib.nv.seckey = secretkey.encode('ascii')
        self.ffimodule.lib.nv.baseurl = baseurl.encode('ascii')
        self.ffimodule.lib.nv.version = '1'.encode('ascii')
        smplintbytes = pack("<H", smplintervalmins)
        self.ffimodule.lib.nv.smplintervalmins = smplintbytes
        self.eepromba = eeprom.Eeprom(64)

        @self.ffimodule.ffi.def_extern()
        def nt3h_writetag(eepromblk, blkdata):
            self.eepromba.write_block(eepromblk, blkdata)
            return 0

        @self.ffimodule.ffi.def_extern()
        def nt3h_readtag(eepromblk, blkdata):
            self.eepromba.read_block(eepromblk, blkdata)
            return 0

        @self.ffimodule.ffi.def_extern()
        def nt3h_eepromwritedone():
            return 0

        @self.ffimodule.ffi.def_extern()
        def printint(myint):
            print("printint " + str(myint))
            return 0

    def check(self):
        return self.ffimodule.ffi.cast("int", 12)


class InstrumentedNDEF(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12):
        super(InstrumentedNDEF, self).__init__(ndefpy, baseurl, serial, secretkey, smplintervalmins)


class InstrumentedOctet(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12):
        super(InstrumentedOctet, self).__init__(octetpy, baseurl, serial, secretkey, smplintervalmins)


class InstrumentedSmplHist(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12):
        super(InstrumentedSmplHist, self).__init__(smplhistpy, baseurl, serial, secretkey, smplintervalmins)


class InstrumentedSample(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12):
        super(InstrumentedSample, self).__init__(samplepy, baseurl, serial, secretkey, smplintervalmins)

        @self.ffimodule.ffi.def_extern()
        def prng_getrandom(lenbits):
            return 16

        @self.ffimodule.ffi.def_extern()
        def batv_measure():
            return 2500

    def tempsample(self, countermax, counterstep):
        counter = 0
        while True:
            counter += counterstep
            counter = counter % countermax
            rawtemp = int((counter + 40) * 4096 / 165)
            yield {'adc': rawtemp, 'ref': counter}

    def rhsample(self, countermax, counterstep):
        counter = 0
        while True:
            counter += counterstep
            counter = counter % countermax
            rawrh = int((counter * 4096) / 100)
            yield {'adc': rawrh, 'ref': counter}


class InstrumentedSampleT(InstrumentedSample):
    def __init__(self,
                 serial='ABCDEFGH',
                 secretkey='AAAACCCC',
                 baseurl='plotsensor.com',
                 smplintervalmins=12):
        super(InstrumentedSampleT, self).__init__(baseurl, serial, secretkey, smplintervalmins)
        temponly = True
        self.ffimodule.lib.sample_init(0, False, temponly)

    def pushsamples(self, num):
        inlist = list()
        tempgen = self.tempsample(100, 0.3)
        for i in range(0, num):
            tempsmpl = next(tempgen)
            inlist.insert(0, {'temp': tempsmpl['ref']})
            self.ffimodule.lib.sample_push(tempsmpl['adc'], 0)
        return inlist


class InstrumentedSampleTRH(InstrumentedSample):
    def __init__(self,
                 serial='ABCDEFGH',
                 secretkey='AAAACCCC',
                 baseurl='plotsensor.com',
                 smplintervalmins=12
                 ):
        super(InstrumentedSampleTRH, self).__init__(baseurl, serial, secretkey, smplintervalmins)
        temponly = False
        self.ffimodule.lib.sample_init(0, False, temponly);

    def pushsamples(self, num):
        inlist = list()
        tempgen = self.tempsample(100, 1.0)
        rhgen = self.rhsample(100, 1.0)
        for i in range(0, num):
            tempsmpl = next(tempgen)
            rhsmpl = next(rhgen)
            inlist.insert(0, {'temp': tempsmpl['ref'], 'rh': rhsmpl['ref']})
            self.ffimodule.lib.sample_push(tempsmpl['adc'], rhsmpl['adc'])
        return inlist

    def geturlqs(self):
        return self.eepromba.get_url_parsedqs()
