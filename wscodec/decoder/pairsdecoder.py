from .exceptions import MessageIntegrityError, DelimiterNotFoundError
from .b64decode import b64decode
import struct
from datetime import timedelta
import hashlib
import hmac

BYTES_PER_SAMPLE = 3
PAIRS_PER_DEMI = 2
ENDSTOP_BYTE = '~'  # This must be URL Safe


class Pair:
    def __init__(self, rd0Msb: int, rd1Msb: int, Lsb: int):
        self.rd0Msb = rd0Msb
        self.rd1Msb = rd1Msb
        self.Lsb = Lsb

        rd0Lsb = (self.Lsb >> 4) & 0xF
        rd1Lsb = self.Lsb & 0xF
        self.rd0 = ((self.rd0Msb << 4) | rd0Lsb)
        self.rd1 = ((self.rd1Msb << 4) | rd1Lsb)

    def __repr__(self):
        return self.readings()

    def readings(self):
        return {'rd0': self.rd0, 'rd1': self.rd1}


class PairsDecoder:
    """
    Unwrap the circular buffer and return a list of pairs

    First the endstop marker is found, which is the character '~'.

    Next the marker is replaced with '=' and combined with the 3 bytes preceeding it.
    These are base64 decoded to yield the minutes elapsed since the
    previous sample and a psuedorandom number.

    The circular buffer is made linear by concatenating the two parts of the buffer
    either side of the end stop.

    3 bytes are popped from the end of the linear buffer. These contain information
    such as the HMAC and the number of valid samples.

    The remaining data in the linear buffer are shaped into a list of 8 byte chunks
    (these should be renamed to Demis).

    Starting from the newest demi, each is decoded into a 6 byte chunk.

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

    def __init__(self, encstr, secretkey, status, usehmac, scandatetime):
        # Split query string at the end of the endstop marker.
        splitend = encstr.split(ENDSTOP_BYTE)

        if len(splitend) != 2:
            raise DelimiterNotFoundError(encstr)

        endmarkerpos = len(splitend[0])

        # Extract the rest of the 4 byte endstop marker xxx~. Replace the marker with '='
        # to make this valid base64.
        # https://stackoverflow.com/questions/7983820/get-the-last-4-characters-of-a-string
        endmarker = splitend[0][-3:] + '='
        splitend[0] = splitend[0][:-3]

        decmarkerbytes = b64decode(endmarker)
        decmarker = int.from_bytes(decmarkerbytes, byteorder='little')
        minuteoffset = decmarker

        endbuf = list()
        declist = list()
        pairlist = list()
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
            decodedchunk = b64decode(chunk)
            declist.append(decodedchunk)

        # Concatenate the decoded endstop bytes.
        endbytes = b''.join([dec for dec in declist])

        # Extract the number of samples and the HMAC/MD5 checksum from the endstop.
        npairsbytes = endbytes[7:9]
        md5bytes = endbytes[0:7]
        urlMD5 = md5bytes.hex()
        npairs = struct.unpack(">H", npairsbytes)[0]

        # Convert 4 byte chunks into 8 byte chunks.
        # There should not be any 4 byte chunks left over,
        # but these should be discarded.
        for i in range(len(linbuf)%2, len(linbuf), 2):
            x = linbuf[i] + linbuf[i+1]
            linbuf8.append(x)

        # The newest 8 byte chunk might only contain
        # 1 valid pair. If so, this is a
        # partial packet and it is processed first.
        rem = npairs % PAIRS_PER_DEMI
        full = int(npairs / PAIRS_PER_DEMI)

        if rem != 0:
            chunk = linbuf8.pop()
            pairs = self.pairsfromchunk(chunk, rem)
            pairlist.extend(pairs)

        # Process remaining full demis. These all contain 2 pairs.
        for i in range(full, 0, -1):
            chunk = linbuf8.pop()
            pairs = self.pairsfromchunk(chunk, 3)
            pairlist.extend(pairs)

        frame = bytearray()

        for pair in pairlist:
            frame.append(pair.rd0Msb)
            frame.append(pair.rd1Msb)
            frame.append(pair.Lsb)

        frame.append(status.loopcount >> 8)
        frame.append(status.loopcount & 0xFF)
        frame.append(status.resetsalltime >> 8)
        frame.append(status.resetsalltime & 0xFF)
        frame.append(status.batv_resetcause >> 8)
        frame.append(status.batv_resetcause & 0xFF)
        frame.append(endmarkerpos >> 8)
        frame.append(endmarkerpos & 0xFF)

        # Perform message authentication.
        calcMD5 = self.gethash(frame, usehmac, bytearray(secretkey, 'utf8'))

        # Truncate calculated MD5 to the same length as the URL MD5.
        calcMD5 = calcMD5[0:len(urlMD5)]

        if urlMD5 == calcMD5:
            self.md5 = urlMD5
        else:
            raise MessageIntegrityError(calcMD5, urlMD5)

        self.pairs = pairlist
        self.npairs = len(pairlist)
        self.endmarkerpos = endmarkerpos
        self.minuteoffset = minuteoffset
        self.newestdatetime = scandatetime - timedelta(minutes=self.minuteoffset) # Timestamp of the newest sample


    def applytimestamp(self, smpls, timeintminutes):
        # Append timestamps to each sample.
        # Start by ordering samples from newest to oldest.
        # The newest sample has the timestamp for now.
        # Each consecutive timestamp decrements the timestamp by the
        # time interval contained inside the URL.
        intervalminutes = timedelta(minutes=timeintminutes)   # Time between samples in seconds
        sampleindex = 0
        for smpl in smpls:
            smpl['ts'] = self.newestdatetime - sampleindex * intervalminutes
            sampleindex = sampleindex + 1
        return smpls

    def chunkstring(self, string, length):
        return (string[i:i+length] for i in range(0, len(string), length))

    # Obtain samples from a 4 byte base64 chunk. Chunk should be renamed to demi here.
    def pairsfromchunk(self, chunk, samplecount):
        chunksamples = list()
        decodedchunk = b64decode(chunk)
        for i in range(0, (samplecount*2)-1, BYTES_PER_SAMPLE):
            rd0Msb = decodedchunk[i]
            rd1Msb = decodedchunk[i+1]
            Lsb = decodedchunk[i+2]

            pair = Pair(rd0Msb, rd1Msb, Lsb)
            chunksamples.append(pair)
        # Return newest sample first.
        chunksamples.reverse()
        return chunksamples

    def gethash(self, message, usehmac, secretkey=None):
        if usehmac:
            hmacobj = hmac.new(secretkey, message, "md5")
            digest = hmacobj.hexdigest()
        else:
            digest = hashlib.md5(message).hexdigest()
        return digest