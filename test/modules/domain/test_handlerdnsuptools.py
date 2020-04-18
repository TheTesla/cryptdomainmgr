#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
import subprocess as sp

testdomain = "test.entroserv.de"
testns = "ns2.inwx.de"

class TestHandlerDNSUptools(unittest.TestCase):
    def testDNSUptoolsUpdate(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomaingmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        ip4=none \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomaingmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        ip4=0.0.0.2,0.0.0.1\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first ip4"):
            self.assertRegex(stdout, ".*add.*new.*0.0.0.2.*")
        with self.subTest("check second ip4"):
            self.assertRegex(stdout, ".*add.*new.*0.0.0.1.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomaingmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        ip4=0.0.0.4,0.0.0.3\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first ip4"):
            self.assertRegex(stdout, ".*add.*new.*0.0.0.4.*")
        with self.subTest("check second ip4"):
            self.assertRegex(stdout, ".*add.*new.*0.0.0.3.*")
        with self.subTest("check previous first ip4"):
            self.assertRegex(stdout, ".*delete.*0.0.0.2.*")
        with self.subTest("check previous second ip4"):
            self.assertRegex(stdout, ".*delete.*0.0.0.1.*")
