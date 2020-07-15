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
    def testDNSUptoolsUpdateIP4(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        ip4=none \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
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
        statedir=/tmp/test_cryptdomainmgr \
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

    def testDNSUptoolsUpdateIP6(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        ip6=none \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        ip6=86::1,23f0::23:42\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first ip6 a"):
            self.assertRegex(stdout, ".*add.*new.*86::1.*")
        with self.subTest("check second ip6 a"):
            self.assertRegex(stdout, ".*add.*new.*23f0::23:42.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        ip6=0f::00,fe00:2345::0\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first ip6 b"):
            self.assertRegex(stdout, ".*add.*new.*0f::00.*")
        with self.subTest("check second ip6 b"):
            self.assertRegex(stdout, ".*add.*new.*fe00:2345::0.*")
        with self.subTest("check previous first ip6"):
            self.assertRegex(stdout, ".*delete.*86::1.*")
        with self.subTest("check previous second ip6"):
            self.assertRegex(stdout, ".*delete.*23f0::23:42.*")

    def testDNSUptoolsUpdateMX(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        mx=none \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        mx=mx01.mailbox.example:50,mx02.mailbox.example:10\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first mx a"):
            self.assertRegex(stdout, ".*add.*new.*mx01.mailbox.example.*")
        with self.subTest("check second mx a"):
            self.assertRegex(stdout, ".*add.*new.*mx02.mailbox.example.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        mx.50=mx03.mailbox.example\
        mx.10=mx04.mailbox.example\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first mx b"):
            self.assertRegex(stdout, ".*add.*new.*mx03.mailbox.example.*")
        with self.subTest("check second mx b"):
            self.assertRegex(stdout, ".*add.*new.*mx04.mailbox.example.*")
        with self.subTest("check previous first mx"):
            self.assertRegex(stdout, ".*delete.*mx01.mailbox.example.*")
        with self.subTest("check previous second mx"):
            self.assertRegex(stdout, ".*delete.*mx02.mailbox.example.*")

    def testDNSUptoolsUpdateSRV(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        srv=none \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        srv=testsrv.entroserv.de:50:10:25:tcp:smtp\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first srv a"):
            self.assertRegex(stdout, ".*add.*new.*_smtp._tcp.test.entroserv.de\
                              : 10 25 testsrv.entroserv.de.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        srv.smtp=mx03.mailbox.example\
        srv.imap=mx04.mailbox.example\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first srv b"):
            self.assertRegex(stdout, ".*add.*new.*mx03.mailbox.example.*")
        with self.subTest("check second srv b"):
            self.assertRegex(stdout, ".*add.*new.*mx04.mailbox.example.*")
        with self.subTest("check previous first srv"):
            self.assertRegex(stdout, ".*delete.*mx01.mailbox.example.*")
        with self.subTest("check previous second srv"):
            self.assertRegex(stdout, ".*delete.*mx02.mailbox.example.*")

    def testDNSUptoolsUpdateSPF(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        spf= \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        spf+=+mx,~all,?aaaa,-ip4:0.1.2.3/24 \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first spf a"):
            self.assertRegex(stdout, ".*add.*new.*mx.*aaaa.*ip4.*all.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        spf=+ip6:00fe::1234:0000/64,-aaaa\
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first spf b"):
            self.assertRegex(stdout, ".*add.*new.*ip6.*aaaa.*")
        with self.subTest("check previous first spf"):
            self.assertRegex(stdout, ".*delete.*mx.*aaaa.*ip4.*all.*")

    def testDNSUptoolsUpdateADSP(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        adsp= \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        adsp=all \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first adsp a"):
            self.assertRegex(stdout, ".*add.*new.*ADSP.*dkim=all.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        adsp=unknown \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first adsp b"):
            self.assertRegex(stdout, ".*update.*ADSP.*dkim=unknown.*")

    def testDNSUptoolsUpdateCAA(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        caa= \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        caa=0 issue test.example \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first caa a"):
            self.assertRegex(stdout, ".*add.*new.*CAA.*issue.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        caa=1 issuewild test2.exmaple \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first caa b"):
            self.assertRegex(stdout, ".*update.*CAA.*issuewild.*")

    def testDNSUptoolsUpdateDMARC(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        dmarc= \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        dmarc.p=quarantine \
        dmarc.pct=100 \
        dmarc.rua=mailto:post@example.org \
        dmarc.ruf=mailto:forensik@example.org \
        dmarc.adkim=s \
        dmarc.aspf=r \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first dmarc a"):
            self.assertRegex(stdout, ".*add.*new.*DMARC.*_dmarc.*p=quarantine.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        dmarc.sp=quarantine \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first dmarc b"):
            self.assertRegex(stdout, ".*update.*DMARC.*sp=quarantine.*")


    def testDNSUptoolsUpdateACME(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        acme= \
        ' 2>&1".format(testdomain), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        acme=test \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first adsp a"):
            self.assertRegex(stdout, ".*add.*new.*ACME.*test.*")

        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        acme= \
        ' 2>&1".format(testdomain), shell=True)
        stdout = str(stdout, "utf-8")
        with self.subTest("check first aucme b"):
            self.assertRegex(stdout, ".*delete.*ACME.*test.*")
