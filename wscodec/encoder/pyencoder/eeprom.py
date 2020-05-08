import ndef
import urllib.parse as urlparse

class Eeprom():
    """
     EEPROM class
    """
    def __init__(self, sizeblocks):
        self.eepromba = bytearray(sizeblocks*16)
        self.sizeblocks = sizeblocks

    def write_block(self, block, blkdata):
        blkstartbyte = block*16
        for i in range(0,16):
            self.eepromba[blkstartbyte + i] = int.from_bytes(blkdata[i], byteorder="little")

    def read_block(self, block, blkdata):
        blkstartbyte = block*16
        blkendbyte = blkstartbyte + 16
        for i in range(0,16):
            blkdata[i] = bytes(self.eepromba[blkstartbyte+i:blkstartbyte+i+1])
        return 0

    def display_block(self, block):
        blkstartbyte = block*16
        blkendbyte = blkstartbyte + 16
        return self.eepromba[blkstartbyte:blkendbyte]

    def __repr__(self):
        retstr = "EEPROM with " + str(self.sizeblocks) + " blocks\n"
        for block in range(0,self.sizeblocks):
            retstr += "EEPROM block " + str(block) + "\n"
            blkstartbyte = block*16
            blkendbyte = blkstartbyte + 16
            retstr += str(self.eepromba[blkstartbyte:blkendbyte]) + "\n"
        return retstr

    def get_message(self):
        ndefmsgstartbyte = 16 + 4
        return self.eepromba[ndefmsgstartbyte:]

    def decode_ndef(self):
        sizedemis = self.sizeblocks * 2
        ndefmessage = self.get_message()
        ndefdemis = bytearray()
        for i in range(0,sizedemis):
            startbyte = i*8
            endbyte = startbyte + 8
            demi = ndefmessage[startbyte:endbyte]
            ndefdemis += demi
        ndefrecords = ndef.message_decoder(ndefdemis)
        # Use next to generate the first record from the ndefrecords generator
        return next(ndefrecords)

    def get_url(self):
        ndefmessage = self.decode_ndef()
        return ndefmessage.iri

    def get_url_parsed(self):
        url = self.get_url()
        return urlparse.urlparse(url)

    def get_url_parsedqs(self):
        parsedurl = self.get_url_parsed()
        urlquery = parsedurl.query
        return urlparse.parse_qs(urlquery)

    def get_qparam(self):
        parsedqs = self.get_url_parsedqs()
        q = parsedqs['q']
        return q[0]

    def get_qdemis(self):
        qstr = self.get_qparam()
        n = 8
        qdemis = [qstr[i:i+n] for i in range(0, len(qstr), n)]
        return qdemis
