from .b64decode import b64decode
import struct

BIT0 = 0x01
BIT1 = 0x02
BIT2 = 0x04
BIT3 = 0x08
BIT4 = 0x10
BIT5 = 0x20
BIT6 = 0x40
BIT7 = 0x80

BOR_BIT = BIT0
SVSH_BIT = BIT1
WDT_BIT = BIT2
MISC_BIT = BIT3
LPM5WU_BIT = BIT4
CLOCKFAIL_BIT = BIT5
SCANTIMEOUT_BIT = BIT7


class StatDecoder():
    def __init__(self, encstr):
        decstr = b64decode(encstr)
        declist = struct.unpack("HHH", decstr)
        self.loopcount = declist[0]
        self.resetsalltime = declist[1]
        self.batv_resetcause = declist[2]

        brownout = (self.batv_resetcause & BOR_BIT) > 0
        supervisor = (self.batv_resetcause & SVSH_BIT) > 0
        watchdog = (self.batv_resetcause & WDT_BIT) > 0
        misc = (self.batv_resetcause & MISC_BIT) > 0
        lpm5wakeup = (self.batv_resetcause & LPM5WU_BIT) > 0
        clockfail = (self.batv_resetcause & CLOCKFAIL_BIT) > 0
        scantimeout = (self.batv_resetcause & SCANTIMEOUT_BIT) > 0

        self.status = {
            "brownout": brownout,
            "supervisor": supervisor,
            "watchdog": watchdog,
            "misc": misc,
            "lpm5wakeup": lpm5wakeup,
            "clockfail": clockfail,
            "scantimeout": scantimeout
        }

    def get_batvoltageraw(self):
        return self.batv_resetcause >> 8

    def get_resetcause(self):
        return self.batv_resetcause & 0xFF

    def get_batvoltagemv(self):
        return (256 * 1500) / self.get_batvoltageraw()

if __name__ == '__main__':
    def x():
        print(StatDecoder("AAABAUsM").status)


    x()
