import ndef
import urllib.parse as urlparse
from ctypes import c_char_p


class Eeprom():
    """
    A mock of the NT3H2111 EEPROM, based on a bytearray. There are methods to read and write from this in 16-byte blocks.
    Helper methods parse the entire EEPROM contents as an NDEF message. This mimics what a phone will do when it reads
    the NT3H2111 using NFC.

    The EEPROM will normally contain the output of the cupl Encoder: an NDEF message containing one NDEF record.
    This itself will contain a URL. One of the parameters in the query string is 'q', which contains the circular
    buffer of temperature and relative humidity samples.
    """
    def __init__(self, sizeblocks: int):
        """
        Instatiate a mock EEPROM.

        :param sizeblocks: Size of the EEPROM in 16-byte blocks.
        """
        self.eepromba = bytearray(sizeblocks*16)
        self.sizeblocks = sizeblocks

    def write_block(self, block: int, blkdata: c_char_p):
        """
        Write one block from a pointer.

        :param block: Address of the block to write
        :param blkdata: Pointer to an array of 16 bytes that will be written to the block.
        :return: None
        """
        blkstartbyte = block*16
        for i in range(0,16):
            self.eepromba[blkstartbyte + i] = int.from_bytes(blkdata[i], byteorder="little")

    def read_block(self, block: int, blkdata: c_char_p):
        """
        Read one block into a pointer.

        :param block: Address if the block to read.
        :param blkdata: Pointer to an array of 16 bytes that the block will be read into.
        :return: None
        """
        blkstartbyte = block*16
        for i in range(0,16):
            blkdata[i] = bytes(self.eepromba[blkstartbyte+i:blkstartbyte+i+1])
        return 0

    def display_block(self, block: int) -> bytearray:
        """
        Display one EEPROM block.

        :param block: Address of the block to display.
        :return: Block data as a list of 16 bytes.
        """
        blkstartbyte = block*16
        blkendbyte = blkstartbyte + 16
        return self.eepromba[blkstartbyte:blkendbyte]

    def __repr__(self) -> str:
        """
        Display all EEPROM blocks.

        :return: The contents of all EEPROM blocks as a string.
        """
        retstr = "EEPROM with " + str(self.sizeblocks) + " blocks\n"
        for block in range(0, self.sizeblocks):
            retstr += "EEPROM block " + str(block) + "\n"
            blkstartbyte = block*16
            blkendbyte = blkstartbyte + 16
            retstr += str(self.eepromba[blkstartbyte:blkendbyte]) + "\n"
        return retstr

    def get_message(self) -> bytearray:
        """
        Extract the NDEF message bytes from EEPROM.

        :return: NDEF message bytearray
        """
        ndefmsgstartbyte = 16 + 4
        return self.eepromba[ndefmsgstartbyte:]

    def decode_ndef(self) -> ndef.Record:
        """
        Decode the NDEF message.

        :return: First NDEF record in the message
        """
        sizedemis = self.sizeblocks * 2
        ndefmessage = self.get_message()
        # Copy NDEF message into a bytearray
        ndefdemis = bytearray()
        for i in range(0,sizedemis):
            startbyte = i*8
            endbyte = startbyte + 8
            demi = ndefmessage[startbyte:endbyte]
            ndefdemis += demi
        # Decode the bytearray.
        ndefrecords = ndef.message_decoder(ndefdemis)
        # Use next to generate the first record from the ndefrecords generator
        return next(ndefrecords)

    def get_url(self) -> str:
        """
        Obtain URL from the NDEF record stored in EEPROM.

        :return: URL string
        """
        ndefmessage = self.decode_ndef()
        return ndefmessage.iri

    def get_url_parsed(self) -> urlparse.ParseResult:
        """
        Parse URL in the EEPROM NDEF record.

        :return: Parsed URL
        """
        url = self.get_url()
        return urlparse.urlparse(url)

    def get_url_parsedqs(self) -> dict:
        """
        Parse parameters in the `query string <https://en.wikipedia.org/wiki/Query_string>`_

        :return: A dictionary of URL parameters.
        """
        parsedurl = self.get_url_parsed()
        urlquery = parsedurl.query
        return urlparse.parse_qs(urlquery)

    def get_qparam(self) -> str:
        """
        :return: The value of URL parameter 'q' as a string.
        """
        parsedqs = self.get_url_parsedqs()
        q = parsedqs['q']
        return q[0]

    def get_qdemis(self) -> list:
        """
        :return: The value of URL parameter 'q' as a list of 8-byte demis.
        """
        qstr = self.get_qparam()
        n = 8
        qdemis = [qstr[i:i+n] for i in range(0, len(qstr), n)]
        return qdemis
