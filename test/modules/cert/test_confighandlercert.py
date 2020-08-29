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

class TestCertconfighandler(unittest.TestCase):
    def testNoSection(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testCertDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[cert]'])
        procConfig(cr)
        self.assertEqual({'caa': {'flag': '0', 'tag': 'issue', 'url': 'letsencrypt.org'}, 'extraflags': [], 'handler': 'dehydrated/letsencrypt', 'keysize': 4096}, cr.config['cert']['DEFAULT'])

    def testCertDefaultSectionDehydratedLetsencryptset(self):
        cr = ConfigReader()
        cr.setContentList(['[cert]\nhandler = dehydrated/letsencrypt \nemail = cdm@cdm.example \nkeysize = 4096 \ndestination = /etc/ssl2 \nextraflags = -x , --hsts \ncertname = full.crt '])
        procConfig(cr)
        self.assertEqual({'keysize': 4096, 'extraflags': ['-x', '--hsts'], 'handler': 'dehydrated/letsencrypt', 'email': 'cdm@cdm.example', 'destination': '/etc/ssl2', 'certname': 'full.crt', 'caa': {'url': 'letsencrypt.org', 'flag': '0', 'tag': 'issue'}}, cr.config['cert']['DEFAULT'])


if "__main__" == __name__:
    unittest.main()


