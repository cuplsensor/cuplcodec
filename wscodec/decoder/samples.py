from .pairs import PairsURL
from .b64decode import B64Decoder
from datetime import timedelta, timezone, datetime


class Sample:
    def __init__(self, timestamp):
        self.timestamp = timestamp


class SamplesURL(PairsURL):
    def __init__(self, *args, timeintb64: str, scandatetime: datetime = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeintb64 = timeintb64
        self.scandatetime = scandatetime or datetime.now(timezone.utc)

        # Calculates the time interval in minutes from a URL parameter.
        timeintbytes = B64Decoder.b64decode(self.timeintb64)
        self.timeintervalmins = int.from_bytes(timeintbytes, byteorder='little')

        self.intervalminutes = timedelta(minutes=self.timeintervalmins)  # Time between samples in seconds
        self.newestdatetime = self.scandatetime - timedelta(minutes=self.elapsedmins)  # Timestamp of the newest sample
        self.samples = list()


    def applytimestamp(self):
        # Append timestamps to each sample.
        # Start by ordering samples from newest to oldest.
        # Each consecutive timestamp decrements the timestamp by the
        # time interval contained inside the URL.
        sampleindex = 0
        for sample in self.samples:
            sample.timestamp = self.newestdatetime - sampleindex * self.intervalminutes
            sampleindex = sampleindex + 1
