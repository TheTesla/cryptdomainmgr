#!/usr/bin/python
# -*- coding: utf-8 -*-

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

    def testCDMDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[cdm]'])
        procConfig(cr)
        self.assertEqual({'cdm': {'statedir': '/var/cryptdomainmgr'}}, cr.config)

    def testCDMDefaultSectionSimpleVal(self):
        cr = ConfigReader()
        cr.setContentList(['[cdm]\nx=3\n'])
        procConfig(cr)
        self.assertEqual({'cdm': {'statedir': '/var/cryptdomainmgr', 'x': '3'}}, cr.config)

    def testCDMDefaultSectionSimpleVal2(self):
        cr = ConfigReader()
        cr.setContentList(['[cdm] \n x = 3 \n '])
        procConfig(cr)
        self.assertEqual({'cdm': {'statedir': '/var/cryptdomainmgr', 'x': '3'}}, cr.config)

    def testCDMDefaultSectionDefaultOverwrite(self):
        cr = ConfigReader()
        cr.setContentList([' [cdm] \n statedir = /blub \n '])
        procConfig(cr)
        self.assertEqual({'cdm': {'statedir': '/blub'}}, cr.config)


if "__main__" == __name__:
    unittest.main()


