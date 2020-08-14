#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan@entroserv.de>
#
#######################################################################

import unittest
import subprocess as sp


class TestMain(unittest.TestCase):
    def testMainHelp(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr -h", shell=True)
        print(stdout[:5])
        self.assertEqual(b"usage", stdout[:5])

    def testMainCDMupdate(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 --config-content \
                                 '[cdm]    statedir=/tmp/test_cryptdomainmgr' \
                                 2>&1", shell=True)
        self.assertIn("update", stdout.decode())

    def testMainCDMupdateFile(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        self.assertIn("update", stdout.decode())

    def testMainCDMprepareFile(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        self.assertIn("prepare", stdout.decode())

    def testMainCDMrolloverFile(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        self.assertIn("rollover", stdout.decode())

    def testMainCDMcleanupFile(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        self.assertIn("cleanup", stdout.decode())

    def testMainCDMnextFile(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        with self.subTest("prepare"):
            self.assertIn("prepare", stdout.decode())

        stdout = sp.check_output("python3 -m cryptdomainmgr \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        with self.subTest("rollover"):
            self.assertIn("rollover", stdout.decode())

        stdout = sp.check_output("python3 -m cryptdomainmgr \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        with self.subTest("cleanup"):
            self.assertIn("cleanup", stdout.decode())
