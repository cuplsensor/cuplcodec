#  cuplcodec encodes environmental sensor data into a URL and the reverse.
#
#  https://github.com/cuplsensor/cuplcodec
#
#  Original Author: Malcolm Mackay
#  Email: malcolm@plotsensor.com
#  Website: https://cupl.co.uk
#
#  Copyright (C) 2021. Plotsensor Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cuplcodec",
    version="2.0.9",
    author="Malcolm Mackay",
    author_email="malcolm@plotsensor.com",
    description="Package for creating and decoding URLs that contain temperature and humidity samples.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cuplsensor/cuplcodec",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
    ],
    include_package_data=True,
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["wscodec/encoder/pyencoder/sample_builder.py:ffibuilder",
                  "wscodec/encoder/pyencoder/ndef_builder.py:ffibuilder",
                  "wscodec/encoder/pyencoder/demi_builder.py:ffibuilder",
                  "wscodec/encoder/pyencoder/pairhist_builder.py:ffibuilder"],
    install_requires=["cffi>=1.0.0", "ndeflib>=0.3.2"],
)
