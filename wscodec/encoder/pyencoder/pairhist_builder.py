from wscodec.encoder.pyencoder import unitc

ffibuilder = unitc.load('pairhist', ['eep', 'md5', 'nvtype'])

if __name__ == "__main__":
    ffibuilder.compile()