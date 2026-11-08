#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# Local end-to-end tests for the openssl (cryptography-based) DKIM key
# handler using the mock domain handler: key generation, DNS TXT record
# publication of the public key and rollover deployment. No rspamd and
# no sudo required, runs fully offline.

import unittest
import os
import re
import shutil
import base64
from cryptography.hazmat.primitives import serialization
from test.test_config import testdomain, tmpdir
from cryptdomainmgr.modules.common.cdmprochelper import runCmd

tmpdirDkim = "/tmp/test_cryptdomainmgr_dkim"


class TestHandlerOpensslDKIM(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(tmpdirDkim, ignore_errors=True)

    def testHandlerOpensslDKIMCreateKey(self):
        conf = '\n'.join([
            "[cdm]", "statedir=" + tmpdirDkim,
            "[domain]", "handler=mock", "mockstore=" + tmpdirDkim + "/mockdns.json",
            "[domain:" + testdomain + "]", "dkim.mydkim=auto",
            "[dkim]", "handler=openssl",
            "[dkim:mydkim]", "keysize=2048",
            "keybasename=key", "keyname=dkimfile.key", "keylocation=" + tmpdirDkim + "/dkim"])
        stdout = runCmd("python3 -m cryptdomainmgr --prepare --config-content '{}' 2>&1".format(conf))

        keyFile = os.path.join(tmpdirDkim, "modules", "dkim", "mydkim", "key", "dkim.key")
        with self.subTest("check key file is created"):
            self.assertTrue(os.path.isfile(keyFile))
        with self.subTest("check key file has correct permissions"):
            self.assertEqual(0o600, os.stat(keyFile).st_mode & 0o777)
        with self.subTest("check DNS TXT record published"):
            # the record content is the base64 DER SubjectPublicKeyInfo
            with open(keyFile, 'rb') as f:
                key = serialization.load_pem_private_key(f.read(), password=None)
            expectedP = base64.b64encode(key.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo)).decode()
            self.assertRegex(stdout, r".*add \(new\) DKIM for .*\.{}.*v=DKIM1.*k=rsa.*p={}".format(
                testdomain, re.escape(expectedP)))

        # rollover: key deployed to the configured location
        runCmd("python3 -m cryptdomainmgr --rollover --config-content '{}' 2>&1".format(conf))

        with self.subTest("check key deployed to keylocation"):
            self.assertTrue(os.path.isfile(os.path.join(tmpdirDkim, "dkim", "dkimfile.key")))
        with self.subTest("check deployed key matches generated key"):
            self.assertTrue(os.path.isfile(keyFile))
            with open(keyFile, 'rb') as fSrc, open(os.path.join(tmpdirDkim, "dkim", "dkimfile.key"), 'rb') as fDst:
                self.assertEqual(fSrc.read(), fDst.read())
