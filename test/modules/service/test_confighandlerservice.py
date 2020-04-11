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

class TestServiceconfighandler(unittest.TestCase):
    def testNoSection(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testServiceDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[service]'])
        procConfig(cr)
        # maybe trash - ToDo: check if needed
        self.assertEqual({'cert': [], 'dhparam': [], 'dkim': []}, cr.config['service']['DEFAULT'])

    def testServiceDefaultApache2set(self):
        cr = ConfigReader()
        cr.setContentList(['[service:apache2]'])
        procConfig(cr)
        # maybe trash - ToDo: check if needed
        self.assertEqual({'cert': [], 'dhparam': [], 'dkim': []}, cr.config['service']['apache2'])

    def testServiceDefaultPostfixset(self):
        cr = ConfigReader()
        cr.setContentList(['[service:postfix]'])
        procConfig(cr)
        # maybe trash - ToDo: check if needed
        self.assertEqual({'cert': [], 'dhparam': [], 'dkim': []}, cr.config['service']['postfix'])


if "__main__" == __name__:
    unittest.main()

