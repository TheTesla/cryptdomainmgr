#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os

# integration tests hitting the real INWX API and LetsEncrypt only run
# when the credentials file is present (never committed); CI skips them
INWXCREDSPRESENT = os.path.isfile("test_inwxcreds.conf")
NOINWXCREDS = "INWX credentials test_inwxcreds.conf not available (live integration test, skipped)"

# test domain must be publicly delegated; test42.bahn.cf (the historical
# test domain) is no longer delegated (NXDOMAIN), so live tests use a
# subdomain of entroserv.de now, see exampleconf/example_acme.conf
testdomain = "test.entroserv.de"
testns = "ns2.inwx.de"
tmpdir="/tmp/test_cryptdomainmgr"
testcertpath = os.path.join(tmpdir, "ssl")
testcertemail = "stefan.helmert@t-online.de"
testdh = "dh512"
dhfile = os.path.join(tmpdir,"myssl/dh512.pem")
