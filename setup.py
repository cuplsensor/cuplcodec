import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cuplcodec",
    version="1",
    author="Malcolm Mackay",
    author_email="malcolm@plotsensor.com",
    description="Package for creating and decoding URLs that contain temperature and humidity samples.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cuplsensor/cuplcodec",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["wscodec/encoder/pyencoder/sample_builder.py:ffibuilder",
                  "wscodec/encoder/pyencoder/ndef_builder.py:ffibuilder",
                  "wscodec/encoder/pyencoder/demi_builder.py:ffibuilder",
                  "wscodec/encoder/pyencoder/pairhist_builder.py:ffibuilder"],
    install_requires=["cffi>=1.0.0", "ndeflib>=0.3.2"],
)
