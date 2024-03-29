#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2021 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import re
import unittest
import subprocess as sp
import os
from test.test_config import testdomain, testns, tmpdir, testcertpath, testcertemail
from cryptography.hazmat.primitives import serialization
import OpenSSL
import getpass
import time
from cryptdomainmgr.modules.common.cdmprochelper import runCmd

keybasename = "key"
keysize = 2048
keyname = "dkimfile.key"
keylocation = "/tmp/test_cryptdomainmgr/dkim"
signingConfDestFile = "/etc/rspamd/local.d/dkim_signing.conf"


def numberOfFiles(path):
    return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

class TestDKIMemailSigning(unittest.TestCase):
    def testDKIMemailSigningSimple(self):
        stdout = runCmd("python3 -m cryptdomainmgr --prepare \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        dkim.mydkim=auto \
        [dkim] \
        handler=rspamd \
        [dkim:mydkim] \
        signingconfdestinationfile={} \
        keybasename={} \
        keysize={} \
        keyname={} \
        keylocation={} \
        [service:rspamd] \
        dkim=mydkim \
        ' 2>&1".format(tmpdir,testdomain,signingConfDestFile,keybasename,keysize,keyname,keylocation))



        stdout = runCmd("python3 -m cryptdomainmgr --rollover \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        dkim.mydkim=auto \
        [dkim] \
        handler=rspamd \
        [dkim:mydkim] \
        signingconfdestinationfile={} \
        keybasename={} \
        keysize={} \
        keyname={} \
        keylocation={} \
        [service:rspamd] \
        dkim=mydkim \
        ' 2>&1".format(tmpdir,testdomain,signingConfDestFile,keybasename,keysize,keyname,keylocation))


        time.sleep(10) # wait until rspamd reloads

        username = getpass.getuser()

        stdout = runCmd("sendmail {}@localhost <<EOF\nsubject: test\ncdmtestrspamd\n\n.\n\nEOF\n 2>&1".format(username))


        time.sleep(10) # wait until email is received by the mailbox

        with open("/var/mail/{}".format(username), "r") as f:
            mail = f.read()


        with open(os.path.join(tmpdir,"modules/dkim","mydkim","conf","dkim.conf"), 'r') as f:
            confStr = f.read()
        dkimSelector =  confStr.split("selector")[1].split("=")[1].split("\"")[1]

        with self.subTest("check if dkim selector in mails"):
            self.assertIn(dkimSelector, mail)


#        stdout = runCmd("python3 -m cryptdomainmgr --cleanup \
#                                 test_inwxcreds.conf --config-content \
#        '\
#        [cdm] \
#        statedir={} \
#        [domain] \
#        handler=dnsuptools/inwx \
#        [domain:{}] \
#        cert=mycert \
#        [cert] \
#        handler=dehydrated/letsencrypt \
#        email={} \
#        keysize=4096 \
#        [cert:mycert] \
#        destination={} \
#        extraflags=--staging,-x \
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath))
#
#        with self.subTest("check current cert is not deleted"):
#            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))
#
#
#    def testHandlerDehydratedCreateMultiCert(self):
#        stdout = runCmd("python3 -m cryptdomainmgr --prepare \
#                                 test_inwxcreds.conf --config-content \
#        '\
#        [cdm] \
#        statedir={} \
#        [domain] \
#        handler=dnsuptools/inwx \
#        [domain:{}] \
#        cert=mycert,mycert2 \
#        [cert] \
#        handler=dehydrated/letsencrypt \
#        email={} \
#        keysize=4096 \
#        [cert:mycert] \
#        destination={} \
#        extraflags=--staging,-x \
#        [cert:mycert2] \
#        destination={} \
#        extraflags=--staging,-x \
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))
#
#        with self.subTest("check cert file is created in tmp 1"):
#            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))
#        with self.subTest("check cert file is created in tmp 2"):
#            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain,certname)))
#        with self.subTest("check if correct number of files are created 1"):
#            self.assertEqual(14,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain)))
#        with self.subTest("check if correct number of files are created 2"):
#            self.assertEqual(14,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain)))
#            # 14 not 12, because csr files
#
#        stdout = runCmd("python3 -m cryptdomainmgr --rollover \
#                                 test_inwxcreds.conf --config-content \
#        '\
#        [cdm] \
#        statedir={} \
#        [domain] \
#        handler=dnsuptools/inwx \
#        [domain:{}] \
#        cert=mycert,mycert2 \
#        [cert] \
#        handler=dehydrated/letsencrypt \
#        email={} \
#        keysize=4096 \
#        [cert:mycert] \
#        destination={} \
#        extraflags=--staging,-x \
#        [cert:mycert2] \
#        destination={} \
#        extraflags=--staging,-x \
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))
#
#        with self.subTest("check cert file is copied to destination 1"):
#            self.assertTrue(os.path.isfile(os.path.join(testcertpath,testdomain,certname)))
#        with self.subTest("check cert file is copied to destination 2"):
#            self.assertTrue(os.path.isfile(os.path.join(testcertpath+"2",testdomain,certname)))
#        with self.subTest("check if correct number of files in destination dir 1 before cleanup"):
#            self.assertEqual(14,numberOfFiles(os.path.join(testcertpath,testdomain)))
#        with self.subTest("check if correct number of files in destination dir 2 before cleanup"):
#            self.assertEqual(14,numberOfFiles(os.path.join(testcertpath+"2",testdomain)))
#            # 14 not 12, because csr files
#
#
#        stdout = runCmd("python3 -m cryptdomainmgr --cleanup \
#                                 test_inwxcreds.conf --config-content \
#        '\
#        [cdm] \
#        statedir={} \
#        [domain] \
#        handler=dnsuptools/inwx \
#        [domain:{}] \
#        cert=mycert,mycert2 \
#        [cert] \
#        handler=dehydrated/letsencrypt \
#        email={} \
#        keysize=4096 \
#        [cert:mycert] \
#        destination={} \
#        extraflags=--staging,-x \
#        [cert:mycert2] \
#        destination={} \
#        extraflags=--staging,-x \
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))
#
#        with self.subTest("check current cert is not deleted 1 in source dir"):
#            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))
#        with self.subTest("check if correct number of files in source dir 1 after cleanup"):
#            self.assertEqual(8,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain)))
#        with self.subTest("check current cert is not deleted 2 in source dir"):
#            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain,certname)))
#        with self.subTest("check if correct number of files in source dir 2 after cleanup"):
#            self.assertEqual(8,numberOfFiles(os.path.join(tmpdir,"modules/cert","mycert2","certs",testdomain)))
#        with self.subTest("check current cert is not deleted 1 in destination dir"):
#            self.assertTrue(os.path.isfile(os.path.join(testcertpath,testdomain,certname)))
#        with self.subTest("check if correct number of files in destination dir 1 after cleanup"):
#            self.assertEqual(8,numberOfFiles(os.path.join(testcertpath,testdomain)))
#        with self.subTest("check current cert is not deleted 2 in destination dir"):
#            self.assertTrue(os.path.isfile(os.path.join(testcertpath+"2",testdomain,certname)))
#        with self.subTest("check if correct number of files in destination dir 2 after cleanup"):
#            self.assertEqual(8,numberOfFiles(os.path.join(testcertpath+"2",testdomain)))
#


if "__main__" == __name__:
    unittest.main()


