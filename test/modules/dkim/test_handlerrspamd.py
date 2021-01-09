#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import re
import unittest
import subprocess as sp
import os
from test.test_config import testdomain, testns, tmpdir, testcertpath, testcertemail
from cryptography.hazmat.primitives import serialization
import OpenSSL

keybasename = "key"
keysize = 2048
keyname = "dkimfile.key"
keylocation = "/tmp/test_cryptdomainmgr/dkim"
signingConfDestFile = os.path.join(tmpdir,"etc/rspamd/local.d/dkim_signing.conf")


def numberOfFiles(path):
    return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

class TestHandlerRspamd(unittest.TestCase):
    def testHandlerRspamdCreateDKIMkey(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
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
        ' 2>&1".format(tmpdir,testdomain,signingConfDestFile,keybasename,keysize,keyname,keylocation), shell=True)

        with self.subTest("check dkim key file is created in tmp"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/dkim","mydkim","key","dkim.key")))
        with self.subTest("check dkim conf file is created in tmp"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/dkim","mydkim","conf","dkim.conf")))

        with open(os.path.join(tmpdir,"modules/dkim","mydkim","conf","dkim.conf"), 'r') as f:
            confStr = f.read()
        dkimSelector =  confStr.split("selector")[1].split("=")[1].split("\"")[1]

        with open(os.path.join(tmpdir,"modules/dkim","mydkim","key","dkim.key"),'r') as f:
            privKeyStr = f.read()
        privKey = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, privKeyStr)
        privKeyCrypto = privKey.to_cryptography_key()
        pubKey = privKeyCrypto.public_key()
        pubKeyStr = pubKey.public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)
        pubKeyStrContent = pubKeyStr.decode('utf8').replace('\n','').split('-----BEGIN PUBLIC KEY-----')[1].split('-----END PUBLIC KEY-----')[0]
        dkimpubkey = re.escape(pubKeyStrContent[:253]+'\\n\\t'+pubKeyStrContent[253:])


        stdout = str(stdout, "utf-8")
        with self.subTest("check dkim keyname"):
            self.assertTrue(dkimSelector[:len(keybasename)] == keybasename)
            self.assertRegex(stdout, ".*add.*new.*DKIM.*{}._domainkey.{}.*{}.*".format(dkimSelector,testdomain,dkimpubkey))
        with self.subTest("check add dkim mydkim"):
            self.assertRegex(stdout, ".*add.*new.*DKIM.*{}._domainkey.{}.*{}.*".format(dkimSelector,testdomain,dkimpubkey))
            #self.assertRegex(stdout, ".*add.*new.*DKIM.*{}.*._domainkey.{}.*".format(keybasename,testdomain))

        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
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
        ' 2>&1".format(tmpdir,testdomain,signingConfDestFile,keybasename,keysize,keyname,keylocation), shell=True)

        with self.subTest("check dkim key file is copied to destination"):
            self.assertTrue(os.path.isfile(os.path.join(keylocation,keyname)))
        with self.subTest("check dkim conf file is copied to destination"):
            self.assertTrue(os.path.isfile(signingConfDestFile))


#        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
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
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath), shell=True)
#
#        with self.subTest("check current cert is not deleted"):
#            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/cert","mycert","certs",testdomain,certname)))
#
#
#    def testHandlerDehydratedCreateMultiCert(self):
#        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
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
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)
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
#        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
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
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)
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
#        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
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
#        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)
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

