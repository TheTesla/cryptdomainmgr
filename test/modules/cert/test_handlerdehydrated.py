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
from test.test_config import testdomain, testns, tmpdir, testcertpath, testcertemail

certname = "fullchain.pem"


class TestHandlerDehydrated(unittest.TestCase):
    def testHandlerDehydratedCreateCert(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath), shell=True)

        with self.subTest("check cert file is created in tmp"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))


        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath), shell=True)

        with self.subTest("check cert file is copied to destination"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath,testdomain,certname)))


        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath), shell=True)

        with self.subTest("check current cert is not deleted"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))


    def testHandlerDehydratedCreateMultiCert(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)

        with self.subTest("check cert file is created in tmp 1"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))
        with self.subTest("check cert file is created in tmp 2"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain,certname)))

        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)

        with self.subTest("check cert file is copied to destination 1"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath,testdomain,certname)))
        with self.subTest("check cert file is copied to destination 2"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath+"2",testdomain,certname)))


        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)

        with self.subTest("check current cert is not deleted 1"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))
        with self.subTest("check current cert is not deleted 2"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain,certname)))


if "__main__" == __name__:
    unittest.main()

