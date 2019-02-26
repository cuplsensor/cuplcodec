from .statdecoder import StatDecoder
from .htdecoder import HTDecoder
from .tdecoder import TDecoder
from .exceptions import UrlDecoderError
import base64

class MissingArgError(UrlDecoderError):
    """
    Missing parameter in the URL query string error.

    """
    errormsg = "Missing Argument {}"

    def __init__(self, arg):
        super().__init__()
        self.arg = arg

    def __str__(self):
        return self.errormsg.format(self.arg)

class UrlDecoder():
    """
    Construct a UrlDecoder object

    Parameters
    -----------
    secretkey
        Secret Key string.

    **reqargs
        A list of query string parameters

    """
    def __init__(self, secretkey, statb64, timeintb64, circb64, ver):
        # Compare md5, scancount and loopcount to determine if this is a duplicate
        self.status = StatDecoder(statb64)

        ver = ver.lstrip('0')  # Remove leading zeroes used for padding
        ver = int(ver)  # Convert to an integer

        if ver == 1:
            dec = HTDecoder
        elif ver == 2:
            dec = TDecoder
        else:
            raise ValueError()

        self.version = ver
        self.timeint = self.timeinterval(timeintb64)
        self.decoded = dec(circb64, True, timeintminutes=self.timeint, secretkey=secretkey)

    def getarg(self, arg, reqargs):
        """
        Get a parameter by name from a list of query string parameters.

        Raises an error if no key is found.

        Parameters
        -----------

        arg
            Name of the parameter to find.

        reqargs
            List of parameters.

        Returns
        --------
        str
            Value of the parameter from the list.

        """
        if arg in reqargs:
            argval = reqargs.get(arg)[0]
        else:
            raise MissingArgError(arg)
        return argval

    def timeinterval(self, enctimeint):
        """
        Get the time interval in minutes from a URL parameter.

        Parameters
        -----------

        enctimeint
            Time interval in little endian byte order encoded as base64.

        Returns
        --------
        int
            Time interval in minutes

        """
        timeintbytes = base64.urlsafe_b64decode(enctimeint)
        timeint = int.from_bytes(timeintbytes, byteorder='little')
        return timeint

if __name__ == '__main__':
    import urllib.parse as urlparse
    testurl = "http://plotsensor.com/?t=AWg=&s=YWJjZGVm&v=01&x=AAABALEK&q=dxx4HHcddh12HXUddRx0HHQddB1zHHMdcxxzHXIdchxxHnEecR1xHnEfcB5wHnAdcB5vH28ebx9vH24fbh5uH24ebh5uH24gbSBuHm0gbSBtIW0gbSBtIG0hbSBsIGwhbCFtIGwgbCBsIGwgbB9sIGwfbCBsIWwhbCBsIWwfbCBsIGwgbB9sH2wfbCBsH2webSBsIGwfbCBsH2wfbCBsIGwhbCFrIGsgayBrIWsgax9qIWohaiBqIGohaiBqIGohaiFpImkhaSBpIWkhaiBuH3Iecx11HXYcdxx4Gnkaehl7GXwYfRh9GH4XfxiAF4EYgReBF4EWgRZ-F3wYexh6GXkZeRp5G3gbeBp4GXcbdxp3Gncbdxt3Gncbdxt3G3cbdxt3G3cbdxt2G3Ybdht2G3Yadht2G3YcdRx1HHUcdRt1G3UbdRt1G3UbdRt0G3QcdBt0HHQcdBx0G3QcdBt0G3QadBt0HHQadBt0HHQcdBt0G3MbcxxzHHMbcxxzHHMbcxxzHHMccxxzHHMccxtzG3MccxtzHHMccxtzHHMccxxyHHMccxxyHHIcchtyHHMbcxx0HXQddR12HXcddxx4HXgceRx6HHocexx7HHwbfBt8G30afRx8HHgbcBtwH3Qddht3G3cbdxp3Gncadxp4GngZeBl4GXgZeBh4GHgZeBkAAAAAwO5Mg9VXLgEA____MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw"
    parsedurl = urlparse.urlparse(testurl)
    urlquery = parsedurl.query
    par = urlparse.parse_qs(urlquery)

    urldecoder = UrlDecoder()
    print(urldecoder.decode(**par))
