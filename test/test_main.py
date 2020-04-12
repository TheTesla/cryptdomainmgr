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


#    def testEmptyConfigContentList(self):
#        cr = ConfigReader()
#        cr.setContentList([])
#        procConfig(cr)
#        self.assertEqual(cr.config, {})

