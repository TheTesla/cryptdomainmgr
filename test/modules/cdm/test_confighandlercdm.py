#!/usr/bin/python
# -*- coding: utf-8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


import unittest
import copy

from cryptdomainmgr.cdmconfighandler import ConfigReader


defaultConfig = {'cdm': {'DEFAULT': {'cert': [],
                                     'depends': {'cert',
                                                 'dhparam',
                                                 'dkim',
                                                 'domain',
                                                 'service'},
                                     'dhparam': [],
                                     'dkim': [],
                                     'domain': [],
                                     'requires': {'cert': [],
                                                  'dhparam': [],
                                                  'dkim': [],
                                                  'domain': [],
                                                  'service': []},
                                     'service': [],
                                     'statedir': '/var/cryptdomainmgr'}}}


def procConfig(cr):
    cr.open()
    cr.interprete(None)
    return cr

class TestCDMconfighandler(unittest.TestCase):
    maxDiff = None

    def testNoSection(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testCDMDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[cdm]'])
        procConfig(cr)
        res = cr.config
        res['cdm']['DEFAULT']['depends'] = set(res['cdm']['DEFAULT']['depends'])
        self.assertEqual(defaultConfig, res)

    def testCDMDefaultSectionSimpleVal(self):
        cr = ConfigReader()
        cr.setContentList(['[cdm]\nx=3\n'])
        procConfig(cr)
        ref = copy.deepcopy(defaultConfig)
        ref['cdm']['DEFAULT']['x'] = '3'
        res = cr.config
        res['cdm']['DEFAULT']['depends'] = set(res['cdm']['DEFAULT']['depends'])
        self.assertEqual(ref, res)

    def testCDMDefaultSectionSimpleVal2(self):
        cr = ConfigReader()
        cr.setContentList(['[cdm] \n x = 3 \n '])
        procConfig(cr)
        ref = copy.deepcopy(defaultConfig)
        ref['cdm']['DEFAULT']['x'] = '3'
        res = cr.config
        res['cdm']['DEFAULT']['depends'] = set(res['cdm']['DEFAULT']['depends'])
        self.assertEqual(ref, res)

    def testCDMDefaultSectionDefaultOverwrite(self):
        cr = ConfigReader()
        cr.setContentList([' [cdm] \n statedir = /blub \n '])
        procConfig(cr)
        ref = copy.deepcopy(defaultConfig)
        ref['cdm']['DEFAULT']['statedir'] = '/blub'
        res = cr.config
        res['cdm']['DEFAULT']['depends'] = set(res['cdm']['DEFAULT']['depends'])
        self.assertEqual(ref, res)


if "__main__" == __name__:
    unittest.main()


