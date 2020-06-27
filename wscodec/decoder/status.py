from .b64decode import B64Decoder
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


class Status:
    """
        Decode the status string.

        Parameters
        -----------
        statb64:
            Value of the URL parameter that holds status information (after base64 encoding).

    """
    def __init__(self, statb64: str):
        decstr = B64Decoder.b64decode(statb64)
        declist = struct.unpack("HHH", decstr)
        self.loopcount = declist[0]
        self.resetsalltime = declist[1]
        self.batv_resetcause = declist[2]

        brownout = (self.get_resetcauseraw() & BOR_BIT) > 0
        supervisor = (self.get_resetcauseraw() & SVSH_BIT) > 0
        watchdog = (self.get_resetcauseraw() & WDT_BIT) > 0
        misc = (self.get_resetcauseraw() & MISC_BIT) > 0
        lpm5wakeup = (self.get_resetcauseraw() & LPM5WU_BIT) > 0
        clockfail = (self.get_resetcauseraw() & CLOCKFAIL_BIT) > 0
        scantimeout = (self.get_resetcauseraw() & SCANTIMEOUT_BIT) > 0

        self.resetcause = {
            "brownout": brownout,
            "supervisor": supervisor,
            "watchdog": watchdog,
            "misc": misc,
            "lpm5wakeup": lpm5wakeup,
            "clockfail": clockfail,
            "scantimeout": scantimeout
        }

    def get_batvoltageraw(self):
        """

        :return: Battery voltage as an 8-bit value.
        """
        return self.batv_resetcause >> 8

    def get_resetcauseraw(self):
        """

        :return: Reset cause as an 8-bit value.
        """
        return self.batv_resetcause & 0xFF

    def get_batvoltagemv(self):
        """

        :return: Battery voltage converted to mV.
        """
        return (256 * 1500) / self.get_batvoltageraw()


