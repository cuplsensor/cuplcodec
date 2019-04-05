import hashlib
import hmac


class MsgAuth(object):
    def __init__(self):
        super().__init__()

    def gethash2(self, message, usehmac, secretkey=None):
        if usehmac:
            hmacobj = hmac.new(secretkey, message)
            digest = hmacobj.hexdigest()
        else:
            digest = hashlib.md5(message).hexdigest()
        return digest

    def gethash(self, message, secretkey=None):
        # Initialise MD5
        m = hashlib.md5()

        firstmsg = bytearray()
        secondmsg = bytearray()

        if secretkey is not None:
            # Append inner padding to message
            for i in range(0,64,1):
                if i < len(secretkey):
                    skeychar = secretkey[i] ^ 0x36
                    firstmsg.append(skeychar)
                else:
                    firstmsg.append(0x36)
            firstmsg = firstmsg + message
            m.update(firstmsg)
        else:
            # Take MD5 of the message
            m.update(message)

        if secretkey is not None:
            firsthash = m.digest()
            #firsthash = bytearray(firsthash)
            # Re-initialise MD5
            m = hashlib.md5()
            # Append outer padding to message
            for i in range(0,64,1):
                if i < len(secretkey):
                    skeychar = secretkey[i] ^ 0x5C
                    secondmsg.append(skeychar)
                else:
                    secondmsg.append(0x5C)

            secondmsg = secondmsg + firsthash
            m.update(secondmsg)

        return m.hexdigest()

if __name__ == '__main__':
    def test():
        msgauth = MsgAuth()
        digest = msgauth.gethash(bytearray(b"0"), bytearray(b"ABCDEFGHIJKL"))
        print(digest)
        hmacobj = hmac.new(bytearray(b"ABCDEFGHIJKL"), bytearray(b"0"))
        digest2 = hmacobj.hexdigest()
        print(digest2)

    test()
