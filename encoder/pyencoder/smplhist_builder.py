from encoder.pyencoder import unitc

ffibuilder = unitc.load('smplhist', ['md5', 'nvtype'])

if __name__ == "__main__":
    ffibuilder.compile()