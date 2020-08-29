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
    def testNoSection(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testTestDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[test]'])
        procConfig(cr)
        self.assertEqual({'test': {'DEFAULT': {'defaultx': '23', 'defaulty': '42'}}}, cr.config)

    def testTestDefaultSectionSimpleVal(self):
        cr = ConfigReader()
        cr.setContentList(['[test]\nx=3\n'])
        procConfig(cr)
        self.assertEqual({'test': {'DEFAULT': {'defaultx': '23', 'defaulty': '42', 'x': '3'}}}, cr.config)

    def testTestDefaultSectionSimpleOverwrite(self):
        cr = ConfigReader()
        cr.setContentList(['[test]\nx=3\n', '[test]\nx=4\n'])
        procConfig(cr)
        self.assertEqual({'test': {'DEFAULT': {'defaultx': '23', 'defaulty': '42', 'x': '4'}}}, cr.config)

    def testTestDefaultSectionDefaultOverwrite(self):
        cr = ConfigReader()
        cr.setContentList(['[test]\ndefaultx=3\n', '[test]\ndefaulty=4\n'])
        procConfig(cr)
        self.assertEqual({'test': {'DEFAULT': {'defaultx': '3', 'defaulty': '4'}}}, cr.config)

    def testTestSection(self):
        cr = ConfigReader()
        cr.setContentList(['[test]\nx=3\n[test:testsection]\ny=4\n'])
        procConfig(cr)
        self.assertEqual({'test': {'DEFAULT': {'defaultx': '23', 'defaulty': '42', 'x': '3'}, 'testsection': {'defaultx': '23', 'defaulty': '42', 'x': '3', 'y': '4'}}}, cr.config)

    def testTestSectionDefaults(self):
        cr = ConfigReader()
        cr.setContentList(['[test]\ndefaultx=3\n[test:testsection]\ndefaulty=4\n'])
        procConfig(cr)
        self.assertEqual({'test': {'DEFAULT': {'defaultx': '3', 'defaulty': '42'}, 'testsection': {'defaultx': '3', 'defaulty': '4'}}}, cr.config)

    def testTestSectionDefaultsOverwrite(self):
        cr = ConfigReader()
        cr.setContentList(['[test]\ndefaultx=3\n[test:testsection]\ndefaultx=4\n'])
        procConfig(cr)
        self.assertEqual({'test': {'DEFAULT': {'defaultx': '3', 'defaulty': '42'}, 'testsection': {'defaultx': '4', 'defaulty': '42'}}}, cr.config)



if "__main__" == __name__:
    unittest.main()






