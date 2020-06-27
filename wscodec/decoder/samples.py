from .pairs import PairsURL
from .b64decode import B64Decoder
from datetime import timedelta, timezone, datetime


class Sample:
    """
    Sample base class. All samples must contain a timestamp.
    """
    def __init__(self, timestamp: datetime):
        """

        Parameters
        ----------
        timestamp : datetime
            Estimated sample collection time. Accurate to one minute.
        """
        self.timestamp = timestamp


class SamplesURL(PairsURL):
    """
    This holds a list of decoded sensor samples. Each needs a timestamp, but this must be calculated. There
    are no absolute timestamps in the URL. First, all times are relative to scantimestamp (when the tag was
    scanned).

    The URL does contain self.elapsedmins (the minutes elapsed since the newest sample was acquired). This makes it
    possible to calculate self.newest_timestamp, the timestamp of the newest sample.

    Every subsequent sample is taken at a fixed time interval relative to self.newest_timestamp. This time interval
    is decoded from timeintb64 into self.timeinterval.

    Parameters
    ----------
    *args
        Variable length argument list
    timeintb64 : str
        Time interval between samples in minutes, base64 encoded into a 4 character string.
    scantimestamp : datetime
        Time the tag was scanned. It corresponds to the time the URL on the tag is requested from the web server.
    **kwargs
        Keyword arguments to be passed to parent class constructors.
    """
    def __init__(self, *args, timeintb64: str, scantimestamp: datetime = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeintb64 = timeintb64
        self.scantimestamp = scantimestamp or datetime.now(timezone.utc)

        # Calculates the time interval in minutes from a URL parameter.
        timeintmins_bytes = B64Decoder.b64decode(self.timeintb64)
        self.timeintmins_int = int.from_bytes(timeintmins_bytes, byteorder='little')

        # Convert time interval into a timedelta object.
        self.timeinterval = timedelta(minutes=self.timeintmins_int)
        # Calculate the timestamp of the newest sample
        self.newest_timestamp = self.scantimestamp - timedelta(minutes=self.elapsedmins)
        # Define an empty list to hold samples.
        self.samples = list()

    def get_samples_list(self):
        """

        Returns
        -------
        Samples as a list of dictionaries. This is done for compatibility purposes.

        """
        return [vars(sample) for sample in self.samples]

    def generate_timestamp(self):
        """

        Yields
        -------
        A timestamp of a sample, calculated relative to that of the newest sample.

        """
        sampleindex = 0
        while sampleindex < len(self.samples):
            yield self.newest_timestamp - sampleindex * self.timeinterval
            sampleindex = sampleindex + 1
