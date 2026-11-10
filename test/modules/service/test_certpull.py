#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
import shutil
import tempfile
import unittest

from cryptdomainmgr.cdmstatehandler import StateHandler
from cryptdomainmgr.modules.common.cdmcertpull import pullCerts

tmpdir = "/tmp/test_cryptdomainmgr_certpull"


class TestCertPull(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(tmpdir, ignore_errors=True)
        # staged cert result, laid out like the acme handler: timestamped
        # files with stable symlinks pointing to them
        staged = os.path.join(tmpdir, "staged", "20261110_120000")
        os.makedirs(staged)
        self.stagedFiles = {}
        for k in ['fullchainfile', 'chainfile', 'certfile', 'keyfile']:
            real = os.path.join(staged, k + "_20261110")
            with open(real, 'w') as f:
                f.write("content-of-" + k)
            link = os.path.join(staged, k.replace('file', '.pem'))
            os.symlink(os.path.basename(real), link)
            self.stagedFiles[k] = link
        sh = StateHandler()
        certState = sh.getSubstate('cert').getSubstate('mailcert')
        certState.result = dict(self.stagedFiles, san=['mail.example.org'])
        self.sh = sh
        self.serviceConfig = {'cert': ['mailcert'], 'certdestination': os.path.join(tmpdir, "etc", "apache2", "ssl")}

    def testPullCopiesAllCertFilesPerSan(self):
        copied = pullCerts(self.serviceConfig, self.sh)
        dest = os.path.join(tmpdir, "etc", "apache2", "ssl", "mail.example.org")
        self.assertEqual([dest], copied)
        for k in ['fullchainfile', 'chainfile', 'certfile', 'keyfile']:
            name = os.path.basename(self.stagedFiles[k])
            self.assertTrue(os.path.isfile(os.path.join(dest, name)))
            with open(os.path.join(dest, name)) as f:
                self.assertEqual("content-of-" + k, f.read())

    def testPullResolvesSymlinksToTimestampedFile(self):
        pullCerts(self.serviceConfig, self.sh)
        dest = os.path.join(tmpdir, "etc", "apache2", "ssl", "mail.example.org")
        # the symlink target must have been copied, not the symlink itself
        for name in [os.path.basename(self.stagedFiles[k]) for k in self.stagedFiles]:
            self.assertFalse(os.path.islink(os.path.join(dest, name)))

    def testNoCertdestinationIsNoop(self):
        self.serviceConfig['certdestination'] = ''
        self.assertEqual([], pullCerts(self.serviceConfig, self.sh))

    def testAutoCertIsFiltered(self):
        # cert=auto (handler default) resolves to no explicit sections
        self.serviceConfig['cert'] = ['auto']
        self.assertEqual([], pullCerts(self.serviceConfig, self.sh))

    def testCertSectionWithoutResultIsSkipped(self):
        # e.g. a group section skipped by the cert phases
        self.sh.getSubstate('cert').getSubstate('emptycert').result = {}
        self.serviceConfig['cert'] = ['emptycert']
        self.assertEqual([], pullCerts(self.serviceConfig, self.sh))


if "__main__" == __name__:
    unittest.main()
