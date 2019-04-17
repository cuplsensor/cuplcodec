import hashlib
import hmac


class MsgAuth(object):
    def __init__(self):
        super().__init__()

    def gethash(self, message, usehmac, secretkey=None):
        if usehmac:
            hmacobj = hmac.new(secretkey, message, "md5")
            digest = hmacobj.hexdigest()
        else:
            digest = hashlib.md5(message).hexdigest()
        return digest


if __name__ == '__main__':
    def test():
        msgauth = MsgAuth()
        digest = msgauth.gethash(bytearray(b"0"), bytearray(b"ABCDEFGHIJKL"))
        print(digest)
        hmacobj = hmac.new(bytearray(b"ABCDEFGHIJKL"), bytearray(b"0"))
        digest2 = hmacobj.hexdigest()
        print(digest2)

    test()
