#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dnsuptools",
    version="0.0.1",
    author="Stefan Helmert",
    author_email="stefan.helmert@t-online.de",
    description="Software managing certificate, dkim and domain updates automagically.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheTesla/cryptdomainmgrpypi",
    packages=setuptools.find_packages(),
    install_requires=[
        "Jinja2",
        "simpleloggerplus",
        "pyOpenSSL",
        "parse"
    ],
    license = 'https://www.fsf.org/licensing/licenses/agpl-3.0.html',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPLv3 License",
        "Operating System :: OS Independent",
    ],
)

