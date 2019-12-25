from wscodec.encoder.pyencoder import unitc

ffibuilder = unitc.load('octet', ['ndef', 'eep', 'base64', 'nvtype'])

if __name__ == "__main__":
    ffibuilder.compile()