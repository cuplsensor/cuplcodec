from wscodec.encoder.pyencoder import unitc

ffibuilder = unitc.load('sample', ['smplhist', 'md5', 'octet', 'ndef', 'eep', 'base64', 'nvtype'])

if __name__ == "__main__":
    ffibuilder.compile()