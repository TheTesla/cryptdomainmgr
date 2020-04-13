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
                                 '[cdm] statedir=/tmp/test_cryptdomaingmgr' \
                                 2>&1", shell=True)
        self.assertIn("update", str(stdout,"utf-8"))

    def testMainCDMupdateFile(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --update \
                                 test/testconfigfile.conf \
                                 2>&1", shell=True)
        self.assertIn("update", str(stdout,"utf-8"))


#    def testEmptyConfigContentList(self):
#        cr = ConfigReader()
#        cr.setContentList([])
#        procConfig(cr)
#        self.assertEqual(cr.config, {})

