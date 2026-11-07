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

# letsencrypt staging tests additionally need CDM_LIVE_STAGING=1 so they
# run only on demand (rate limits, external service) - e.g. as the last
# step after everything else passed:
#   CDM_LIVE_STAGING=1 python3 -m unittest test.modules.complextests.test_certtlsa
RUN_LIVE_STAGING = os.environ.get("CDM_LIVE_STAGING", "") == "1"
NOLIVESTAGING = "letsencrypt staging test disabled (set CDM_LIVE_STAGING=1 to run it, keep usage rare)"

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
