from encoder.pyencoder import unitc

class Testbench(object):
    def __init__(self,
                modfilename,
                depfilenames
                ):
        self.module, self.ffi, self.filename = unitc.load(modfilename, depfilenames)

class NDEF(Testbench):
    def __init__(self):
        super(NDEF, self).__init__('ndef',
                                   ['eep', 'base64', 'nvtype'])
class Octet(Testbench):
    def __init__(self):
        super(Octet, self).__init__('octet',
                                    ['ndef', 'eep', 'base64', 'nvtype'])
class SmplHist(Testbench):
    def __init__(self):
        super(SmplHist, self).__init__('smplhist',
                                       ['md5', 'nvtype'])
class Sample(Testbench):
    def __init__(self):
        super(Sample, self).__init__('sample',
                                      ['smplhist', 'md5', 'octet', 'ndef', 'eep', 'base64', 'nvtype'])

if __name__ == "__main__":
    ndef = NDEF()
    octet = Octet()
    smplhist = SmplHist()
    sample = Sample()
