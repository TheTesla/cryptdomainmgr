#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cryptdomainmgr",
    version="0.0.9",
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
        "dnsuptools",
        "parse"
    ],
    license = 'https://www.fsf.org/licensing/licenses/agpl-3.0.html',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)

