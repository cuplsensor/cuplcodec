import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name = "urldecoder",
	version = "0.0.3",
	author ="Malcolm Mackay",
	author_email= "malcolm.mackay121@gmail.com",
	description = "Package for decoding URLs that contain temperature and humidity samples.",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url="https://github.com/malcolmmackay/HumidiTag",
	packages=setuptools.find_packages(),
	classifiers=[
        	"Programming Language :: Python :: 3",
        	"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        	"Operating System :: OS Independent",
    	],
)
