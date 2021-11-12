'''Setup script for bidsmapper'''

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="bidsmapper",
    version="1.0.0",
    description="Generates a bidsmap for user-defined XNAT projects as a JSON file.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    author="Real Python",
    author_email="john.gray@nyspi.columbia.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["bidsmapper"],
    include_package_data=True,
    install_requires=[
        "feedparser", "html2text", "importlib_resources", "typing"
    ],
    entry_points={"console_scripts": ["bidsmapper=main.__main__:main"]},
)