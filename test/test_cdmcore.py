#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
import copy

from cryptdomainmgr.cdmcore import getNextPhase, getCurrentPhase, StateHandler, ConfigReader, runPhase, ManagedDomain

def procConfig(cr):
    cr.open()
    cr.interprete(None)
    return cr

class StateTest:
    def __init__(self):
        self.result = {"nextphase": "myphase"}

class TestCDMcore(unittest.TestCase):
    def testGetNextPhase(self):
        self.assertEqual("rollover", getNextPhase("prepare"))
        self.assertEqual("cleanup", getNextPhase("rollover"))
        self.assertEqual("prepare", getNextPhase("cleanup"))
        self.assertEqual("prepare", getNextPhase("update"))
        self.assertEqual("prepare", getNextPhase("blub"))

    def testGetCurrentPhase(self):
        s = StateTest()
        self.assertEqual("myphase", getCurrentPhase(s))
        self.assertEqual("forcedphase", getCurrentPhase(s, "forcedphase"))
        del s.result["nextphase"]
        self.assertEqual("prepare", getCurrentPhase(s))

    def testRunPhase(self):
        sh = StateHandler()
        cr = ConfigReader()
        cr.setContentList(['[test]\nbla = blub\n[test:mytestname]\nbla = blubber'])
        procConfig(cr)
        runPhase(cr, sh, "prepare")
        with self.subTest("<opstate>"):
            self.assertEqual("done", sh.opstate)
        with self.subTest("test/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').opstate)
        with self.subTest("test/DEFAULT/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('DEFAULT').opstate)
        with self.subTest("test/mytestname/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('mytestname').opstate)

    def testManagedDomain(self):
        md = ManagedDomain()
        #md.readConfig(content="[cdm]\nstatedir={}\n[test:mytest]".format(tmpStateFile.name))
        md.run(confContent="[cdm]\nstatedir=/tmp/test_cryptdomainmgr\n[test:mytest]", forcePhase="update")
        sh = md.sh
        with self.subTest("<config>"):
            res = copy.deepcopy(sh.config)
            res['DEFAULT']['depends'] = set(res['DEFAULT']['depends'])
            self.assertEqual({'DEFAULT': {'depends': {'dhparam', 'domain',
                                                      'dkim', 'service',
                                                      'cert'}, 'statedir':
                                          '/tmp/test_cryptdomainmgr'}}, res)
        with self.subTest("<result> (first)"):
            self.assertEqual({'nextphase': 'prepare'}, sh.result)
        md = ManagedDomain()
        md.run(confContent="[cdm]\nstatedir=/tmp/test_cryptdomainmgr\n[test]\n[test:mytestname]")
        sh = md.sh
        with self.subTest("<opstate>"):
            self.assertEqual("done", sh.opstate)
        with self.subTest("test/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').opstate)
        with self.subTest("test/DEFAULT/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('DEFAULT').opstate)
        with self.subTest("test/mytestname/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('mytestname').opstate)
        with self.subTest("<result> (second)"):
            self.assertEqual({'nextphase': 'rollover'}, sh.result)
        md = ManagedDomain()
        md.run(confContent="[cdm]\nstatedir=/tmp/test_cryptdomainmgr\n[test:mytest]")
        sh = md.sh
        with self.subTest("<result> (third)"):
            self.assertEqual({'nextphase': 'cleanup'}, sh.result)
        md = ManagedDomain()
        md.run(confContent="[cdm]\nstatedir=/tmp/test_cryptdomainmgr\n[test:mytest]")
        sh = md.sh
        with self.subTest("<result> (fourth)"):
            self.assertEqual({'nextphase': 'prepare'}, sh.result)

    def testManagedDomainReadConfig(self):
        md = ManagedDomain()
        md.readConfig(confContent="[cdm]\nstatedir=/tmp/test_cryptdomainmgr\n[test]\n[test:mytestname]")
        #md.run(confContent="[cdm]\nstatedir=/tmp/test_cryptdomainmgr\n[test]\n[test:mytestname]")
        md.run(forcePhase='prepare')
        sh = md.sh
        with self.subTest("<opstate>"):
            self.assertEqual("done", sh.opstate)
        with self.subTest("test/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').opstate)
        with self.subTest("test/DEFAULT/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('DEFAULT').opstate)
        with self.subTest("test/mytestname/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('mytestname').opstate)

    def testManagedDomainReadConfig2(self):
        md = ManagedDomain()
        md.readConfig(confContent="  [cdm]  \n  statedir  =  /tmp/test_cryptdomainmgr  \n  [test]  \n  [test:mytestname] ")
        md.run(forcePhase='prepare')
        sh = md.sh
        with self.subTest("<opstate>"):
            self.assertEqual("done", sh.opstate)
        with self.subTest("test/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').opstate)
        with self.subTest("test/DEFAULT/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('DEFAULT').opstate)
        with self.subTest("test/mytestname/<opstate>"):
            self.assertEqual("done", sh.getSubstate('test').getSubstate('mytestname').opstate)

if "__main__" == __name__:
    unittest.main()




