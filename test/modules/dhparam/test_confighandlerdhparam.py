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

class TestDHparamconfighandler(unittest.TestCase):
    def testNoSection(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testDHparamDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[dhparam]'])
        procConfig(cr)
        self.assertEqual({'filename': '/etc/myssl/dhparam.pem', 'keysize': 2048}, cr.config['dhparam']['DEFAULT'])

    def testDHparamDefaultSectionDehydratedLetsencryptset(self):
        cr = ConfigReader()
        cr.setContentList(['[dhparam]\nhandler = openssl \nfilename = /etc/myssl2/dhp.dh \nkeysize = 4096  '])
        procConfig(cr)
        self.assertEqual({'keysize': 4096, 'handler': 'openssl', 'filename': '/etc/myssl2/dhp.dh'}, cr.config['dhparam']['DEFAULT'])

    def testDHparamNamedSectionDehydratedLetsencryptset(self):
        cr = ConfigReader()
        cr.setContentList(['[dhparam:name]\nhandler = openssl \nkeysize = 4096  '])
        procConfig(cr)
        self.assertEqual({'keysize': 4096, 'handler': 'openssl', 'filename': '/etc/myssl/dh2048.pem'}, cr.config['dhparam']['name'])


if "__main__" == __name__:
    unittest.main()


