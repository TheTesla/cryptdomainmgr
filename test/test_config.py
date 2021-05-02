#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os

testdomain = "test42.bahn.cf"
testns = "ns2.inwx.de"
tmpdir="/tmp/test_cryptdomainmgr"
testcertpath = os.path.join(tmpdir, "ssl")
testcertemail = "stefan.helmert@t-online.de"
testdh = "dh512"
dhfile = os.path.join(tmpdir,"myssl/dh512.pem")

