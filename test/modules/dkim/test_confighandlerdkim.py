#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
import os

from cryptdomainmgr.cdmconfighandler import ConfigReader

def procConfig(cr):
    cr.open()
    cr.interprete(None)
    return cr

class TestDKIMconfighandler(unittest.TestCase):
    def testNoSection(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testDKIMDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[dkim]'])
        procConfig(cr)
        self.assertEqual({'keysize': 2048}, cr.config['dkim']['DEFAULT'])

    def testDKIMDefaultSectionRspamdset(self):
        cr = ConfigReader()
        cr.setContentList(['[dkim:maindkim]\nhandler = rspamd \nkeysize = 4096  '])
        procConfig(cr)
        # the signing config rendering moved to the rspamd SERVICE handler
        self.assertEqual({'keysize': '4096', 'handler': 'rspamd', 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'keyname': 'dkim.key'}, cr.config['dkim']['maindkim'])


if "__main__" == __name__:
    unittest.main()


