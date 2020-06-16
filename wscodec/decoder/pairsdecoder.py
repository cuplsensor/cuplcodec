from .exceptions import MessageIntegrityError
from .paramdecoder import ParamDecoder
from .b64decode import b64decode
import struct
from datetime import timedelta
import hashlib
import hmac

BYTES_PER_SAMPLE = 3
PAIRS_PER_DEMI = 2

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


class PairsDecoder(ParamDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pairs = list()
        self.samples = list()
        self.md5 = None
        self.npairs = None
        self.endmarkerpos = None
        self.minuteoffset = None
        self.newestdatetime = None

    def _decode_elapsedb64(self, elapsedb64):
        decmarkerbytes = b64decode(elapsedb64)
        decmarker = int.from_bytes(decmarkerbytes, byteorder='little')
        self.minuteoffset = decmarker

    def decode(self):
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

            """
        super().decode()

        # Extract elapsed minutes since the previous sample in minutes xxx~. Replace the '=' to make this valid base64.
        elapsedb64 = self.linearbuf[-3:] + '='
        # Remove elapsedb64 from the linear buffer.
        self.linearbuf = self.linearbuf[:-3]
        # Decode elapsedb64
        self._decode_elapsedb64(elapsedb64)

        declist = list()
        pairlist = list()

        # Pop the 3 bytes from the end of the buffer.
        # These contain the MD5 hash and the number of valid samples
        endbuf = self.linearbuf[-12:]
        self.linearbuf = self.linearbuf[:-12]
        endbuf4 = self.chunkstring(endbuf, 4)

        # Decode the endstop 4 bytes at a time.
        for chunk in endbuf4:
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
        linbuf8 = self.chunkstring(self.linearbuf, 8)

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

        frame.append(self.status.loopcount >> 8)
        frame.append(self.status.loopcount & 0xFF)
        frame.append(self.status.resetsalltime >> 8)
        frame.append(self.status.resetsalltime & 0xFF)
        frame.append(self.status.batv_resetcause >> 8)
        frame.append(self.status.batv_resetcause & 0xFF)
        frame.append(self.endmarkerpos >> 8)
        frame.append(self.endmarkerpos & 0xFF)

        # Perform message authentication.
        calcMD5 = self.gethash(frame)

        # Truncate calculated MD5 to the same length as the URL MD5.
        calcMD5 = calcMD5[0:len(urlMD5)]

        if urlMD5 == calcMD5:
            self.md5 = urlMD5
        else:
            raise MessageIntegrityError(calcMD5, urlMD5)

        self.pairs = pairlist
        self.npairs = len(pairlist)
        self.newestdatetime = self.scandatetime - timedelta(minutes=self.minuteoffset) # Timestamp of the newest sample

    def applytimestamp(self):
        # Append timestamps to each sample.
        # Start by ordering samples from newest to oldest.
        # The newest sample has the timestamp for now.
        # Each consecutive timestamp decrements the timestamp by the
        # time interval contained inside the URL.
        intervalminutes = timedelta(minutes=self.timeintervalmins)   # Time between samples in seconds
        sampleindex = 0
        for sample in self.samples:
            sample['ts'] = self.newestdatetime - sampleindex * intervalminutes
            sampleindex = sampleindex + 1

    def chunkstring(self, string, n):
        return list(string[i:i+n] for i in range(0, len(string), n))

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

    def gethash(self, message):
        secretkeyba = bytearray(self.secretkey, 'utf8')
        if self.usehmac:
            hmacobj = hmac.new(secretkeyba, message, "md5")
            digest = hmacobj.hexdigest()
        else:
            digest = hashlib.md5(message).hexdigest()
        return digest