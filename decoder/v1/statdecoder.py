import base64
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
        decstr = base64.urlsafe_b64decode(encstr)
        declist = struct.unpack("HBBH", decstr)
        self.loopcount = declist[0]

        self.resetsalltime = declist[1]

        resetcause = declist[2]
        brownout = (resetcause & BOR_BIT) > 0
        supervisor = (resetcause & SVSH_BIT) > 0
        watchdog = (resetcause & WDT_BIT) > 0
        misc = (resetcause & MISC_BIT) > 0
        lpm5wakeup = (resetcause & LPM5WU_BIT) > 0
        clockfail = (resetcause & CLOCKFAIL_BIT) > 0
        scantimeout = (resetcause & SCANTIMEOUT_BIT) > 0

        self.status = {
            "resetsalltime": resetsalltime,
            "brownout": brownout,
            "supervisor": supervisor,
            "watchdog": watchdog,
            "misc": misc,
            "lpm5wakeup": lpm5wakeup,
            "clockfail": clockfail,
            "scantimeout": scantimeout
        }

        self.batvoltagemv = declist[3] # batvoltagerwaw


if __name__ == '__main__':
    def x():
        print(StatDecoder("AAABAUsM").status)

    x()
