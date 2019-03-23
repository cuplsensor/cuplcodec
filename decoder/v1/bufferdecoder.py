import base64
import struct
from .msgauth import MsgAuth
from ..exceptions import DecoderError
from datetime import datetime, timedelta

class MessageIntegrityError(DecoderError):
    errormsg = "MD5 checksum mismatch. Calculated MD5 = {}, URL MD5 = {}"

    def __init__(self, calcmd5, urlmd5):
        super().__init__()
        self.calcmd5 = calcmd5
        self.urlmd5 = urlmd5

    def __str__(self):
        return self.errormsg.format(self.calcmd5, self.urlmd5)

class BufferDecoder(MsgAuth):
    """
    Extract raw sample data from the circular buffer

    First the endstop marker is found, which is the character '~'.

    Next the marker is replaced with '=' and combined with the 3 bytes preceeding it.
    These are base64 decoded to yield the minutes elapsed since the
    previous sample and a psuedorandom number.

    The circular buffer is made linear by concatenating the two parts of the buffer
    either side of the end stop.

    3 bytes are popped from the end of the linear buffer. These contain information
    such as the HMAC and the number of valid samples.

    The remaining data in the linear buffer are shaped into a list of 8 byte chunks
    (these should be renamed to Octets).

    Starting from the newest octet, each is decoded into a 6 byte chunk.

    Either 1 or 2 (3 byte) samples are extracted from every chunk and these
    are written to a list.

    When the complete list of samples have been obtained, the HMAC checksum is
    calculated. This is compared to the HMAC supplied in the URL. These two
    values must match for the decoded data to be valid. If they are, it confirms
    that whatever generated the encoded list of samples must have the secret key.

    Parameters
    -----------
    encstr
        Circular buffer string containing samples and an endstop encoded as base64.

    secretkey
        Secret key used to verify that the circular buffer has originated from a trusted source.

    """
    BYTES_PER_SAMPLE = 3
    SAMPLES_PER_OCTET = 2

    def __init__(self, encstr, secretkey):
        super().__init__()
        # Split query string at the end of the endstop marker.
        splitend = encstr.split('~')

        endmarkerpos = len(splitend[0])

        # Extract the rest of the 4 byte endstop marker xxx~. Replace the marker with '='
        # to make this valid base64.
        # https://stackoverflow.com/questions/7983820/get-the-last-4-characters-of-a-string
        endmarker = splitend[0][-3:] + '='
        splitend[0] = splitend[0][:-3]

        decmarkerbytes = base64.urlsafe_b64decode(endmarker)
        decmarker = int.from_bytes(decmarkerbytes, byteorder='little')
        minuteoffset = decmarker

        smplcounter = 0
        smplcount = 0

        endbuf = list()
        declist = list()
        samplelist = list()
        linbuf8 = list()

        # Linearise the circular buffer.
        circbufstart = list(self.chunkstring(splitend[0], 4))
        circbufend = list(self.chunkstring(splitend[1], 4))

        linbuf = circbufend + circbufstart

        # Pop the 3 bytes from the end of the buffer.
        # These contain the MD5 hash and the number of valid samples
        for i in range(0,3,1):
            endbuf.append(linbuf.pop())
        endbuf.reverse()

        # Decode the endstop 4 bytes at a time.
        for chunk in endbuf:
            decodedchunk = base64.urlsafe_b64decode(chunk)
            declist.append(decodedchunk)

        # Concatenate the decoded endstop bytes.
        endbytes = b''.join([dec for dec in declist])

        # Extract the number of samples and the HMAC/MD5 checksum from the endstop.
        smplcountbytes = endbytes[7:9]
        md5bytes = endbytes[0:7]
        urlMD5 = md5bytes.hex()
        smplcount = struct.unpack(">H", smplcountbytes)[0]

        # Convert 4 byte chunks into 8 byte chunks.
        # There should not be any 4 byte chunks left over,
        # but these should be discarded.
        for i in range(len(linbuf)%2, len(linbuf), 2):
            x = linbuf[i] + linbuf[i+1]
            linbuf8.append(x)

        # The newest 8 byte chunk might only contain
        # 1 valid sample. If so, this is a
        # partial packet and it is processed first.
        rem = smplcount % BufferDecoder.SAMPLES_PER_OCTET
        full = int(smplcount / BufferDecoder.SAMPLES_PER_OCTET)

        if rem != 0:
            chunk = linbuf8.pop()
            smpls = self.samplesfromchunk(chunk, rem)
            samplelist.extend(smpls)

        # Process remaining full packets. These all contain 3 samples.
        for i in range(full, 0, -1):
            chunk = linbuf8.pop()
            print(chunk)
            smpls = self.samplesfromchunk(chunk, 3)
            samplelist.extend(smpls)

        frame = bytearray()

        for sample in samplelist:
            frame.append(sample['tempMsb'])
            frame.append(sample['rhMsb'])
            frame.append(sample['Lsb'])

        # Perform message authentication.
        calcMD5 = super().gethash(frame, bytearray(secretkey, 'utf8'))

        # Truncate calculated MD5 to the same length as the URL MD5.
        calcMD5 = calcMD5[0:len(urlMD5)]

        if urlMD5 == calcMD5:
            self.md5 = urlMD5
        else:
            raise MessageIntegrityError(calcMD5, urlMD5)

        self.rawsmpls = samplelist
        self.rawsmplcount = smplcount
        self.endmarkerpos = endmarkerpos
        self.minuteoffset = minuteoffset
        self.timestamp = datetime.utcnow() - timedelta(minutes=self.minuteoffset)

    def applytimestamp(self, smpls, timeintminutes):
        # Append timestamps to each sample.
        # Start by ordering samples from newest to oldest.
        # The newest sample has the timestamp for now.
        # Each consecutive timestamp decrements the timestamp by the
        # time interval contained inside the URL.
        intervalminutes = timedelta(minutes=timeintminutes)   # Time between samples in seconds
        sampleindex = 0
        for smpl in smpls:
            smpl['ts'] = self.timestamp - sampleindex * intervalminutes
            sampleindex = sampleindex + 1
        return smpls

    def chunkstring(self, string, length):
        substrs = len(string)/length
        return (string[i:i+length] for i in range(0, len(string), length))

    # Obtain samples from a 4 byte base64 chunk. Chunk should be renamed to octet here.
    def samplesfromchunk(self, chunk, samplecount):
        chunksamples = list()
        decodedchunk = base64.urlsafe_b64decode(chunk)
        for i in range(0, (samplecount*2)-1, BufferDecoder.BYTES_PER_SAMPLE):
            tempMsb = decodedchunk[i]
            rhMsb = decodedchunk[i+1]
            Lsb = decodedchunk[i+2]

            smpl = {'tempMsb':tempMsb, 'rhMsb':rhMsb, 'Lsb':Lsb}
            chunksamples.append(smpl)
        # Return newest sample first.
        chunksamples.reverse()
        return chunksamples


if __name__ == '__main__':
    teststr="dxx4HHcddh12HXUddRx0HHQddB1zHHMdcxxzHXIdchxxHnEecR1xHnEfcB5wHnAdcB5vH28ebx9vH24fbh5uH24ebh5uH24gbSBuHm0gbSBtIW0gbSBtIG0hbSBsIGwhbCFtIGwgbCBsIGwgbB9sIGwfbCBsIWwhbCBsIWwfbCBsIGwgbB9sH2wfbCBsH2webSBsIGwfbCBsH2wfbCBsIGwhbCFrIGsgayBrIWsgax9qIWohaiBqIGohaiBqIGohaiFpImkhaSBpIWkhaiBuH3Iecx11HXYcdxx4Gnkaehl7GXwYfRh9GH4XfxiAF4EYgReBF4EWgRZ-F3wYexh6GXkZeRp5G3gbeBp4GXcbdxp3Gncbdxt3Gncbdxt3G3cbdxt3G3cbdxt2G3Ybdht2G3Yadht2G3YcdRx1HHUcdRt1G3UbdRt1G3UbdRt0G3QcdBt0HHQcdBx0G3QcdBt0G3QadBt0HHQadBt0HHQcdBt0G3MbcxxzHHMbcxxzHHMbcxxzHHMccxxzHHMccxtzG3MccxtzHHMccxtzHHMccxxyHHMccxxyHHIcchtyHHMbcxx0HXQddR12HXcddxx4HXgceRx6HHocexx7HHwbfBt8G30afRx8HHgbcBtwH3Qddht3G3cbdxp3Gncadxp4GngZeBl4GXgZeBh4GHgZeBkAAAAAwO5Mg9VXLgEA____MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw"
    def test():
        samples = HTDecoder().getsamples(teststr, True, 8)
        print(samples)

    def testtime():
        timeintb64 = "ZZZ="
        print(HTDecoder().decode_timeinterval(timeintb64))




    test()
