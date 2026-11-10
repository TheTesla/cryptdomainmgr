#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
from cryptdomainmgr.modules.common.cdmconfighelper import applyDefault, applyInheritance

class TestConfighelperInheritance(unittest.TestCase):
    maxDiff = None

    def testApplyDefaultBasic(self):
        config = {
            'DEFAULT': {'handler': 'acme', 'keysize': 4096},
            'mycert': {'keysize': 2048},
            'othercert': {},
        }
        result = applyDefault(config, {'extra': 'x'})
        self.assertEqual('acme', result['mycert']['handler'])
        self.assertEqual(2048, result['mycert']['keysize'])
        self.assertEqual('x', result['mycert']['extra'])
        self.assertEqual(4096, result['othercert']['keysize'])

    def testApplyInheritanceSingleLevel(self):
        config = {
            'DEFAULT': {},
            'cert': {'handler': 'acme', 'keysize': 4096},
            'cert:mail': {'inherit': 'cert', 'destination': '/etc/mail'},
            'cert:web': {'destination': '/etc/web'},
        }
        result = applyInheritance(config)
        self.assertNotIn('inherit', result['cert:mail'])
        self.assertEqual('acme', result['cert:mail']['handler'])
        self.assertEqual('/etc/mail', result['cert:mail']['destination'])
        # sections without inherit stay untouched
        self.assertNotIn('handler', result['cert:web'])

    def testApplyInheritanceMultipleLevels(self):
        # the mail use case: [cert] -> [cert:mail] -> [cert:mail-smtp]
        config = {
            'DEFAULT': {},
            'cert': {'handler': 'acme', 'keysize': 4096, 'email': 'hostmaster@example.org'},
            'cert:mail': {'inherit': 'cert', 'destination': '/etc/mail-certs', 'tlsa.tcp.25': 'auto:3:1:1'},
            'cert:mail-smtp': {'inherit': 'cert:mail', 'keysize': 2048},
            'cert:mail-imap': {'inherit': 'cert:mail'},
        }
        result = applyInheritance(config)
        mailSmtp = result['cert:mail-smtp']
        self.assertEqual('acme', mailSmtp['handler'])                       # from [cert] (2 levels up)
        self.assertEqual('hostmaster@example.org', mailSmtp['email'])      # from [cert]
        self.assertEqual('/etc/mail-certs', mailSmtp['destination'])       # from [cert:mail]
        self.assertEqual('auto:3:1:1', mailSmtp['tlsa.tcp.25'])            # from [cert:mail]
        self.assertEqual(2048, mailSmtp['keysize'])                        # own key wins
        self.assertNotIn('inherit', mailSmtp)
        self.assertEqual('/etc/mail-certs', result['cert:mail-imap']['destination'])
        # parent sections keep their own resolved content
        self.assertEqual('/etc/mail-certs', result['cert:mail']['destination'])

    def testApplyInheritanceMultipleParents(self):
        config = {
            'DEFAULT': {},
            'base': {'a': 'from-base', 'b': 'from-base'},
            'tlsa': {'tlsa.tcp.25': 'auto:3:1:1', 'b': 'from-tlsa'},
            'cert:mail': {'inherit': 'base, tlsa'},
        }
        result = applyInheritance(config)
        mail = result['cert:mail']
        self.assertEqual('from-base', mail['a'])
        self.assertEqual('from-tlsa', mail['b'])  # later parent wins

    def testApplyInheritanceErrors(self):
        # cycle
        config = {'a': {'inherit': 'b'}, 'b': {'inherit': 'a'}}
        with self.assertRaises(ValueError):
            applyInheritance(config)
        # self reference
        config = {'a': {'inherit': 'a'}}
        with self.assertRaises(ValueError):
            applyInheritance(config)
        # missing parent
        config = {'a': {'inherit': 'nowhere'}}
        with self.assertRaises(KeyError):
            applyInheritance(config)

    def testApplyInheritanceModuleKeyStripping(self):
        # the config reader strips the '<module>:' prefix before
        # applyDefault sees the config, so references written as in the
        # config file ('cert:mail') must resolve to the internal key
        # ('mail'); bare keys also work
        config = {
            'DEFAULT': {},
            'cert': {'keysize': 4096},
            'mail': {'inherit': 'cert', 'destination': '/etc/mail'},
            'mail-smtp': {'inherit': 'cert:mail'},
            'mail-imap': {'inherit': 'mail'},
        }
        result = applyInheritance(config)
        for sec in ('mail-smtp', 'mail-imap'):
            self.assertEqual(4096, result[sec]['keysize'])
            self.assertEqual('/etc/mail', result[sec]['destination'])
            self.assertNotIn('inherit', result[sec])

    def testApplyInheritanceModuleBaseSection(self):
        # the bare module name ('cert') references the module base section
        # ([cert], stored as 'DEFAULT' internally)
        config = {
            'DEFAULT': {'keysize': 4096, 'email': 'h@x.org'},
            'mail': {'inherit': 'cert', 'destination': '/etc/mail'},
            'mail-smtp': {'inherit': 'cert:mail'},
        }
        result = applyInheritance(config, moduleName='cert')
        self.assertEqual(4096, result['mail']['keysize'])
        self.assertEqual('/etc/mail', result['mail']['destination'])
        self.assertEqual('/etc/mail', result['mail-smtp']['destination'])
        self.assertEqual('h@x.org', result['mail-smtp']['email'])

    def testApplyDefaultWithInheritance(self):
        # integration: applyDefault resolves inheritance BEFORE the DEFAULT
        # section and the handler defaults are applied
        config = {
            'DEFAULT': {'handler': 'acme'},
            'cert': {'keysize': 4096},
            'cert:mail': {'inherit': 'cert'},
        }
        result = applyDefault(config)
        self.assertEqual('acme', result['cert:mail']['handler'])  # from DEFAULT
        self.assertEqual(4096, result['cert:mail']['keysize'])    # from [cert]
