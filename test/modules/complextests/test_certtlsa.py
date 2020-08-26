#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
import subprocess as sp
import os

testdomain = "test42.entroserv.de"
testns = "ns2.inwx.de"
testcertpath = "/tmp/test_cryptdomainmgr/ssl"
tmpdir = "/tmp/test_cryptdomainmgr"
testcertemail = "stefan.helmert@t-online.de"


class TestCertTLSA(unittest.TestCase):
    def testCertTLSACreate(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        certname=fullchain.pem \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath), shell=True)

        #print(stdout)
        stdout = str(stdout, "utf-8")
        with self.subTest("check tlsa 3 1 1"):
            self.assertRegex(stdout, ".*add.*new.*_443._tcp.test42.entroserv.de.*3 1 1.*")
        with self.subTest("check tlsa 2 0 1"):
            self.assertRegex(stdout, ".*add.*_443._tcp.test42.entroserv.de.*2 0 1.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        certname=fullchain.pem \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath), shell=True)

        #print(stdout)

        with self.subTest("check cert file exists"):
            self.assertFalse(os.path.isfile(os.path.join(testcertpath,"fullchain.pem")))


        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        certname=fullchain.pem \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath), shell=True)


        #print(stdout)


