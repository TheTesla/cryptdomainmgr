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
from test.test_config import testdomain, testns, tmpdir, testcertpath, testcertemail, INWXCREDSPRESENT, NOINWXCREDS
from cryptography.hazmat.primitives import serialization
from cryptdomainmgr.modules.common.cdmprochelper import runCmd

keybasename = "key"
keysize = 2048
keyname = "dkimfile.key"
keylocation = "/tmp/test_cryptdomainmgr/dkim"
signingConfDestFile = "/tmp/test_cryptdomainmgr/etc/rspamd/local.d/dkim_signing.conf"


def numberOfFiles(path):
    return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

@unittest.skipUnless(INWXCREDSPRESENT, NOINWXCREDS)
class TestHandlerRspamd(unittest.TestCase):
    def testHandlerRspamdCreateDKIMkey(self):
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
        keybasename={} \
        keysize={} \
        keyname={} \
        keylocation={} \
        [service:rspamd] \
        handler=rspamd \
        dkim=mydkim \
        reload=false \
        signingconfdestinationfile={} \
        ' 2>&1".format(tmpdir,testdomain,keybasename,keysize,keyname,keylocation,signingConfDestFile))

        sp.check_output(('sudo', 'chmod', '+r', os.path.join(tmpdir,"modules/dkim","mydkim","key","dkim.key")))
        with self.subTest("check dkim key file is created in tmp"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdir,"modules/dkim","mydkim","key","dkim.key")))

        # the selector comes from the published DNS record - the signing
        # conf is rendered by the rspamd SERVICE handler at rollover
        selectorMatch = re.search(r"add \(new\) DKIM for (key_\d+)\._domainkey\.", stdout)
        self.assertIsNotNone(selectorMatch)
        dkimSelector = selectorMatch.group(1)

        with open(os.path.join(tmpdir,"modules/dkim","mydkim","key","dkim.key"),'r') as f:
            privKeyStr = f.read()
        privKey = serialization.load_pem_private_key(privKeyStr.encode(), password=None)
        pubKey = privKey.public_key()
        pubKeyStr = pubKey.public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)
        pubKeyStrContent = pubKeyStr.decode('utf8').replace('\n','').split('-----BEGIN PUBLIC KEY-----')[1].split('-----END PUBLIC KEY-----')[0]
        dkimpubkey = re.escape(pubKeyStrContent)


        with self.subTest("check dkim keyname"):
            self.assertTrue(dkimSelector[:len(keybasename)] == keybasename)
            self.assertRegex(stdout, ".*add.*new.*DKIM.*{}._domainkey.{}.*{}.*".format(dkimSelector,testdomain,dkimpubkey))
        with self.subTest("check add dkim mydkim"):
            self.assertRegex(stdout, ".*add.*new.*DKIM.*{}._domainkey.{}.*{}.*".format(dkimSelector,testdomain,dkimpubkey))
            #self.assertRegex(stdout, ".*add.*new.*DKIM.*{}.*._domainkey.{}.*".format(keybasename,testdomain))

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
        keybasename={} \
        keysize={} \
        keyname={} \
        keylocation={} \
        [service:rspamd] \
        handler=rspamd \
        dkim=mydkim \
        reload=false \
        signingconfdestinationfile={} \
        ' 2>&1".format(tmpdir,testdomain,keybasename,keysize,keyname,keylocation,signingConfDestFile))

        with self.subTest("check dkim key file is copied to destination"):
            self.assertTrue(os.path.isfile(os.path.join(keylocation,keyname)))
        with self.subTest("check rspamd signing conf rendered by service handler"):
            self.assertTrue(os.path.isfile(signingConfDestFile))


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

