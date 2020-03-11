#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest

from cryptdomainmgr.cdmconfighandler import *

def procConfig(cr):
    cr.open()
    cr.interprete(None)
    return cr


class TestCDMconfigcandler(unittest.TestCase):
    def testEmptyConfig(self):
        cr = ConfigReader()
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testEmptyConfigContentList(self):
        cr = ConfigReader()
        cr.setContentList([])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testEmptyConfigContentListEntry(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})


if "__main__" == __name__:
    unittest.main()



