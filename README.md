# cuplcodec
[cuplcodec](https://cupl.co.uk/index.php/software/cuplcodec/) encodes environmental sensor data into a URL. Each sample includes two 12-bit readings (temperature and humidity). These are converted to base64 and written into a circular buffer. A HMAC is written after the most recent sample in the buffer. The URL can be rendered as a QR code or stored on an NFC tag. If a tag with a URL is tapped 
by a mobile phone, it opens automatically in a web browser. This allows the user to view sensor data **without installing an app on their phones**. A web application comprising [cuplfrontend](https://github.com/cuplsensor/cuplfrontend) and [cuplbackend](https://github.com/cuplsensor/cuplbackend) runs the decoder in cuplcodec, unwraps the circular buffer and displays a list of samples in the browser.

## Tests

![GitHub Workflow Status](https://github.com/cuplsensor/cuplcodec/workflows/Python%20package/badge.svg)

The codec is tested with [pytest](https://docs.pytest.org/en/stable/). The encoder written in C can be tested with the decoder written in Python using [CFFI](https://cffi.readthedocs.io/en/latest/).

## Documentation 

[![Documentation Status](https://readthedocs.org/projects/wscodec/badge/?version=latest)](https://readthedocs.org/projects/wscodec/badge/?version=latest) 

Hosted on [ReadTheDocs](https://readthedocs.org/projects/wscodec/badge/?version=latest). This includes information on how to run the encoder on an MSP430.

## PyPI Package

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/cuplcodec/)

Hosted on [PyPI](https://pypi.org/project/cuplcodec/). Install the package with: 
         
    pip install cuplcodec
    
## Licence

### cuplcodec

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### Documentation

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
