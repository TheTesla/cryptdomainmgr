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

def numberOfFiles(path):
    return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

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
        with self.subTest("check if correct number of files are created 1"):
            self.assertEqual(14,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain)))
        with self.subTest("check if correct number of files are created 2"):
            self.assertEqual(14,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain)))
            # 14 not 12, because csr files

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
        with self.subTest("check if correct number of files in destination dir 1 before cleanup"):
            self.assertEqual(14,numberOfFiles(os.path.join(testcertpath,testdomain)))
        with self.subTest("check if correct number of files in destination dir 2 before cleanup"):
            self.assertEqual(14,numberOfFiles(os.path.join(testcertpath+"2",testdomain)))
            # 14 not 12, because csr files


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

        with self.subTest("check current cert is not deleted 1 in source dir"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))
        with self.subTest("check if correct number of files in source dir 1 after cleanup"):
            self.assertEqual(8,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain)))
        with self.subTest("check current cert is not deleted 2 in source dir"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain,certname)))
        with self.subTest("check if correct number of files in source dir 2 after cleanup"):
            self.assertEqual(8,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain)))
        with self.subTest("check current cert is not deleted 1 in destination dir"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath,testdomain,certname)))
        with self.subTest("check if correct number of files in destination dir 1 after cleanup"):
            self.assertEqual(8,numberOfFiles(os.path.join(testcertpath,testdomain)))
        with self.subTest("check current cert is not deleted 2 in destination dir"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath+"2",testdomain,certname)))
        with self.subTest("check if correct number of files in destination dir 2 after cleanup"):
            self.assertEqual(8,numberOfFiles(os.path.join(testcertpath+"2",testdomain)))



if "__main__" == __name__:
    unittest.main()

