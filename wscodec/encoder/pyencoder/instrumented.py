#  cuplcodec encodes environmental sensor data into a URL and the reverse.
#
#  https://github.com/cuplsensor/cuplcodec
#
#  Original Author: Malcolm Mackay
#  Email: malcolm@plotsensor.com
#  Website: https://cupl.co.uk
#
#  Copyright (C) 2021. Plotsensor Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from .sharedobj import ndefpy, demipy, pairhistpy, samplepy
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
                 smplintervalmins,
                 batteryadc=100,
                 format=1,
                 resetsalltime=0,
                 usehmac=True,
                 httpsdisable=False
                 ):
        # To remove ambiguity, boolean variables are stored as integers.
        if httpsdisable:
            httpsdisable_int = 1
        else:
            httpsdisable_int = 0

        if usehmac:
            usehmac_int = 1
        else:
            usehmac_int = 0

        self.secretkey = secretkey
        self.ffimodule = ffimodule
        self.ffimodule.lib.nv.serial = serial.encode('ascii')
        self.ffimodule.lib.nv.seckey = secretkey.encode('ascii')
        self.ffimodule.lib.nv.baseurl = baseurl.encode('ascii')
        self.ffimodule.lib.nv.format = bytes([format])
        self.ffimodule.lib.nv.usehmac = usehmac_int
        self.ffimodule.lib.nv.httpsdisable = httpsdisable_int
        self.ffimodule.lib.nv.resetsalltime = resetsalltime
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



class InstrumentedNDEF(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12):
        super(InstrumentedNDEF, self).__init__(ndefpy, baseurl, serial, secretkey, smplintervalmins)


class InstrumentedDemi(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12):
        super(InstrumentedDemi, self).__init__(demipy, baseurl, serial, secretkey, smplintervalmins)


class InstrumentedPairhist(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12):
        super(InstrumentedPairhist, self).__init__(pairhistpy, baseurl, serial, secretkey, smplintervalmins)


class InstrumentedSample(InstrumentedBase):
    def __init__(self,
                 baseurl='plotsensor.com',
                 serial='AAAACCCC',
                 secretkey='AAAACCCC',
                 smplintervalmins=12,
                 batteryadc=100,
                 format=1,
                 resetsalltime=0,
                 usehmac=True,
                 httpsdisable=False
                 ):
        super(InstrumentedSample, self).__init__(samplepy, baseurl, serial, secretkey, smplintervalmins, batteryadc, format, resetsalltime, usehmac, httpsdisable)
        self.set_battery_adc(batteryadc)

        @self.ffimodule.ffi.def_extern()
        def batv_measure():
            return self.batteryadc

    def set_battery_adc(self, batteryadc):
        self.batteryadc = batteryadc

    def get_url(self):
        return self.eepromba.get_url()

    def temp_degc_to_raw(self, degc):
        """ Converts degrees C to a raw ADC value for the Texas HDC2010. """
        return int((degc + 40) * 4096 / 165)

    def rh_percent_to_raw(self, rhpc):
        """ Converts from relative humidity in percent to a raw ADC value for the Texas HDC2010. """
        return int((rhpc * 4096) / 100)

    def tempsample(self, countermax, counterstep):
        counter = 0
        while True:
            counter += counterstep
            counter = counter % countermax
            rawtemp = self.temp_degc_to_raw(counter)
            yield {'adc': rawtemp, 'ref': counter}

    def rhsample(self, countermax, counterstep):
        counter = 0
        while True:
            counter += counterstep
            counter = counter % countermax
            rawrh = self.rh_percent_to_raw(counter)
            yield {'adc': rawrh, 'ref': counter}

    def pushsamplelist(self, trhlist: list):
        """

        :param trhlist: a list of dictionaries each containing temperature and relative humidity keys.
        :return: None
        """
        for smpldict in trhlist:
            tempdegc = smpldict['temp']
            rhpc = smpldict['rh']
            tempraw = self.temp_degc_to_raw(tempdegc)
            rhraw = self.rh_percent_to_raw(rhpc)
            # rhraw is ignored (set to -1) inside enc_pushsample if the format is temperature only.
            self.ffimodule.lib.enc_pushsample(tempraw, rhraw)

    def updateendstop(self, minutes: int):
        """ Update the endstop with minutes elapsed since the most recent sample.

        :param minutes: Minutes elapsed since the most recent sample.
        :return: None
        """
        self.ffimodule.lib.enc_setelapsed(minutes)


class InstrumentedSampleT(InstrumentedSample):
    FORMAT_HDC2021_TEMPONLY = 2

    def __init__(self,
                 serial='ABCDEFGH',
                 secretkey='AAAACCCC11112222',
                 baseurl='plotsensor.com',
                 smplintervalmins=12,
                 resetsalltime=0,
                 batteryadc=100,
                 resetcause=0,
                 usehmac=True,
                 httpsdisable=False,
                 tagerror=False,
                 format=FORMAT_HDC2021_TEMPONLY
                 ):
        super(InstrumentedSampleT, self).__init__(baseurl,
                                                  serial,
                                                  secretkey,
                                                  smplintervalmins,
                                                  batteryadc=batteryadc,
                                                  format=format,
                                                  resetsalltime=resetsalltime,
                                                  usehmac=usehmac,
                                                  httpsdisable=httpsdisable)
        self.ffimodule.lib.enc_init(resetcause, tagerror, 0)

    def pushsamples(self, num):
        inlist = list()
        tempgen = self.tempsample(100, 0.3)
        for i in range(0, num):
            tempsmpl = next(tempgen)
            inlist.insert(0, {'temp': tempsmpl['ref']})
            self.ffimodule.lib.enc_pushsample(tempsmpl['adc'], 0)
        return inlist


class InstrumentedSampleTRH(InstrumentedSample):
    FORMAT_HDC2021_TRH = 1

    def __init__(self,
                 serial='ABCDEFGH',
                 secretkey='AAAACCCC11112222',
                 baseurl='plotsensor.com',
                 smplintervalmins=12,
                 resetsalltime=0,
                 batteryadc=100,
                 resetcause=0,
                 usehmac=True,
                 httpsdisable=False,
                 tagerror=False,
                 format=FORMAT_HDC2021_TRH
                 ):
        super(InstrumentedSampleTRH, self).__init__(baseurl,
                                                    serial,
                                                    secretkey,
                                                    smplintervalmins,
                                                    batteryadc=batteryadc,
                                                    format=format,
                                                    resetsalltime=resetsalltime,
                                                    usehmac=usehmac,
                                                    httpsdisable=httpsdisable)
        self.ffimodule.lib.enc_init(resetcause, tagerror, 0)

    def pushsamples(self, num):
        inlist = list()
        tempgen = self.tempsample(100, 1.0)
        rhgen = self.rhsample(100, 1.0)
        for i in range(0, num):
            tempsmpl = next(tempgen)
            rhsmpl = next(rhgen)
            inlist.insert(0, {'temp': tempsmpl['ref'], 'rh': rhsmpl['ref']})
            self.ffimodule.lib.enc_pushsample(tempsmpl['adc'], rhsmpl['adc'])
        return inlist

    def geturlqs(self):
        return self.eepromba.get_url_parsedqs()
