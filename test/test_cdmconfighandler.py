#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest

from cryptdomainmgr.cdmconfighandler import ConfigReader

def procConfig(cr):
    cr.open()
    cr.interprete(None)
    return cr


class TestCDMconfighandler(unittest.TestCase):
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

    def testAddFilenames(self):
        cr = ConfigReader()
        cr.addFilenames(['a','b','c'])
        cr.addFilenames(['d','e','f'])
        self.assertEqual(cr.filenameList, ['a','b','c','d','e','f'])

    def testSetFilenames(self):
        cr = ConfigReader()
        cr.addFilenames(['a','b','c'])
        cr.addFilenames(['d','e','f'])
        cr.setFilenames(['g','h','i'])
        self.assertEqual(cr.filenameList, ['g','h','i'])

    def testSetContentList(self):
        cr = ConfigReader()
        cr.setContentList(['a','b','c'])
        cr.setContentList(['d','e','f'])
        cr.setContentList(['g','h\nr','i'])
        self.assertEqual(cr.contentList, ['g','h\nr','i'])


if "__main__" == __name__:
    unittest.main()



