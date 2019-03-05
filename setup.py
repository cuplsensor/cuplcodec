import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PSCodec",
    version="0.0.4",
    author="Malcolm Mackay",
    author_email="malcolm.mackay121@gmail.com",
    description="Package for creating and decoding URLs that contain temperature and humidity samples.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/malcolmmackay/PSCodec",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["encoder/pyencoder/sample_builder.py:ffibuilder",
                  "encoder/pyencoder/ndef_builder.py:ffibuilder",
                  "encoder/pyencoder/octet_builder.py:ffibuilder",
                  "encoder/pyencoder/smplhist_builder.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
)
