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
        self.assertEqual({'caa': {'flag': '0', 'tag': 'issue', 'url': 'letsencrypt.org'}, 'extraflags': [], 'handler': 'acme', 'keysize': 4096}, cr.config['cert']['DEFAULT'])

    def testCertLegacyDehydratedTranslatedToAcme(self):
        cr = ConfigReader()
        cr.setContentList(['[cert]\nhandler = dehydrated/letsencrypt \nemail = cdm@cdm.example \nkeysize = 4096 \ndestination = /etc/ssl2 \nextraflags = -x , --hsts \ncertname = full.crt '])
        procConfig(cr)
        # legacy dehydrated configurations are served by the acme handler
        self.assertEqual({'keysize': 4096, 'extraflags': ['-x', '--hsts'], 'handler': 'acme', 'email': 'cdm@cdm.example', 'destination': '/etc/ssl2', 'certname': 'full.crt', 'caa': {'url': 'letsencrypt.org', 'flag': '0', 'tag': 'issue'}}, cr.config['cert']['DEFAULT'])

    def testCertLegacyDehydratedStagingFlagMapsToStagingCA(self):
        cr = ConfigReader()
        cr.setContentList(['[cert]\nhandler = dehydrated/letsencrypt \nemail = cdm@cdm.example \nextraflags = --staging,-x '])
        procConfig(cr)
        self.assertEqual('acme', cr.config['cert']['DEFAULT']['handler'])
        self.assertEqual('https://acme-staging-v02.api.letsencrypt.org/directory', cr.config['cert']['DEFAULT']['ca'])
        self.assertEqual(['-x'], cr.config['cert']['DEFAULT']['extraflags'])

    def testCertLegacyDehydratedNonLetsencryptClearsCaa(self):
        cr = ConfigReader()
        cr.setContentList(['[cert]\nhandler = dehydrated/otherca \nemail = cdm@cdm.example '])
        procConfig(cr)
        self.assertEqual('acme', cr.config['cert']['DEFAULT']['handler'])
        self.assertEqual('', cr.config['cert']['DEFAULT']['caa'])

    def testCertInheritanceChain(self):
        # [cert] -> [cert:mail] (group) -> [cert:mail-smtp] (concrete cert)
        cr = ConfigReader()
        cr.setContentList(['[cert]\nhandler = acme \nemail = cdm@cdm.example \n'
                           '[cert:mail]\ninherit = cert \nkeysize = 2048 \n'
                           '[cert:mail-smtp]\ninherit = cert:mail \ndestination = /etc/mail-smtp \n'])
        procConfig(cr)
        mailSmtp = cr.config['cert']['mail-smtp']
        self.assertEqual('acme', mailSmtp['handler'])              # from [cert], 2 levels up
        self.assertEqual('cdm@cdm.example', mailSmtp['email'])     # from [cert]
        self.assertEqual(2048, mailSmtp['keysize'])                # from [cert:mail]
        self.assertEqual('/etc/mail-smtp', mailSmtp['destination'])  # own
        self.assertNotIn('inherit', mailSmtp)
        # the group section resolves for itself as well
        self.assertEqual(2048, cr.config['cert']['mail']['keysize'])
        self.assertEqual('cdm@cdm.example', cr.config['cert']['mail']['email'])

    def testCertInheritanceMissingParentRaises(self):
        cr = ConfigReader()
        cr.setContentList(['[cert:mail]\ninherit = cert:nowhere'])
        with self.assertRaises(KeyError):
            procConfig(cr)


if "__main__" == __name__:
    unittest.main()


