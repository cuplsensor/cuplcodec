# cuplcodec
[cuplcodec](https://cupl.co.uk/index.php/software/cuplcodec/) encodes environmental sensor data into a URL. Each sample can consist of one or two 12-bit readings (e.g. temperature and humidity). These are converted to base64 and written to a circular buffer. A HMAC is written after the most recent sample in the buffer. The URL can be rendered as a QR code or stored on an NFC tag. If the latter is tapped 
with a mobile phone, it opens automatically in a web browser. A web application comprising [cuplfrontend](https://github.com/cuplsensor/cuplfrontend) and [cuplbackend](https://github.com/cuplsensor/cuplbackend) runs the decoder in cuplcodec, unwraps the circular buffer and displays a list of samples.

## Tests

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/cuplsensor/cuplcodec/Install%20cuplcodec%20and%20run%20tests.)

The codec is tested with [pytest](https://docs.pytest.org/en/stable/).[CFFI](https://cffi.readthedocs.io/en/latest/) provides a Python interface to the encoder written in C.

## Documentation 

[![Documentation Status](https://readthedocs.org/projects/codec/badge/?version=latest)](https://cupl.readthedocs.io/projects/codec/en/latest/?badge=latest) 

Hosted on [ReadTheDocs](https://cupl.readthedocs.io/projects/codec/en/latest/). This includes information on how to run the encoder on an MSP430.

## PyPI Package

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/cuplcodec/)

Hosted on [PyPI](https://pypi.org/project/cuplcodec/). Install the package with: 
         
    pip install cuplcodec
    
## Licence

### cuplcodec

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### Documentation

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
