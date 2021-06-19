#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
import os

from cryptdomainmgr.cdmstatehandler import StateHandler


class TestCDMstatehandler(unittest.TestCase):
    def testEmptyState(self):
        sh = StateHandler()
        self.assertEqual('uninitialized', sh.opstate)

    def testEmptyAllStates(self):
        sh = StateHandler()
        with self.subTest("initial state"):
            self.assertEqual('uninitialized', sh.opstate)
        sh.setOpStateWaiting()
        with self.subTest("wait state"):
            self.assertEqual('waiting', sh.opstate)
        sh.setOpStateRunning()
        with self.subTest("not done state"):
            self.assertFalse(sh.isDone())
        with self.subTest("run state"):
            self.assertEqual('running', sh.opstate)
        sh.setOpStateDone()
        with self.subTest("done state"):
            self.assertTrue(sh.isDone())

    def testRegisterResult(self):
        sh = StateHandler()
        sh.registerResult({'a': 42})
        self.assertEqual({'a': 42}, sh.result)

    def testRegisterConfig(self):
        sh = StateHandler()
        sh.registerConfig({'b': 23})
        self.assertEqual({'b': 23}, sh.config)

    def testDict(self):
        sh = StateHandler()
        with self.subTest("empty to dict"):
            self.assertEqual({'opstate': 'uninitialized', 'result': {}, 'config': {}, 'substate': {}}, sh.toDict())
        with self.subTest("empty to dict"):
            sh.fromDict({'opstate': 'done', 'result': {'b': 23}, 'config': {'c': 42}, 'substate': {}})
            self.assertEqual({'opstate': 'done', 'result': {'b': 23}, 'config': {'c': 42}, 'substate': {}}, sh.toDict())
        with self.subTest("from empty dict"):
            sh.fromDict({})
            self.assertEqual('uninitialized', sh.opstate)

    def testSubstate(self):
        sh = StateHandler()
        ssh1 = sh.getSubstate("mysubstate_1")
        ssh2 = sh.getSubstate("mysubstate_2")
        sssh21 = ssh2.getSubstate("mysubstate_21")
        sssh22 = ssh2.getSubstate("mysubstate_22")
        sssh22.setOpStateDone()
        sssh21.setOpStateWaiting()
        ssh2.setOpStateRunning()
        with self.subTest("set substates"):
            self.assertEqual({'opstate': 'uninitialized', 'result': {}, 'config': {},\
            'substate': {'mysubstate_1': {'opstate': 'uninitialized', 'result': {}, 'config': {}, 'substate': {}},\
                         'mysubstate_2': {'opstate': 'running', 'result': {}, 'config': {}, \
                                          'substate': {'mysubstate_21': {'opstate': 'waiting', 'result': {}, 'config': {}, 'substate': {}}, \
                             'mysubstate_22': {'opstate': 'done', 'result': {}, 'config': {}, 'substate': {}}}}}}, sh.toDict())
        with self.subTest("reset substates"):
            sh.resetOpStateRecursive()
            self.assertEqual({'opstate': 'uninitialized', 'result': {}, 'config': {},\
            'substate': {'mysubstate_1': {'opstate': 'uninitialized', 'result': {}, 'config': {}, 'substate': {}},\
                         'mysubstate_2': {'opstate': 'uninitialized', 'result': {}, 'config': {}, \
                                          'substate': {'mysubstate_21': {'opstate': 'uninitialized', 'result': {}, 'config': {}, 'substate': {}}, \
                             'mysubstate_22': {'opstate': 'uninitialized', 'result': {}, 'config': {}, 'substate': {}}}}}}, sh.toDict())

    def testSubstateSaveLoad(self):
        sh = StateHandler()
        ssh1 = sh.getSubstate("mysubstate_1")
        ssh2 = sh.getSubstate("mysubstate_2")
        sssh21 = ssh2.getSubstate("mysubstate_21")
        sssh22 = ssh2.getSubstate("mysubstate_22")
        sssh22.setOpStateDone()
        sssh21.setOpStateWaiting()
        ssh2.setOpStateRunning()
        sh.config = {'DEFAULT': {'statedir': '/tmp/test_cdmstatehandler'}}
        sh.save()
        ssh1.setOpStateDone()
        sh.save('/tmp/test_cdmstatehandler_2/state2.json')
        shLoad1 = StateHandler()
        shLoad1.load('/tmp/test_cdmstatehandler_2/state2.json')
        with self.subTest("set substates - load direkt"):
            self.assertEqual({'opstate': 'uninitialized', 'result': {},
                              'config': {'DEFAULT': {'statedir':
                                         '/tmp/test_cdmstatehandler'}},\
            'substate': {'mysubstate_1': {'opstate': 'done', 'result': {}, 'config': {}, 'substate': {}},\
                         'mysubstate_2': {'opstate': 'running', 'result': {}, 'config': {}, \
                                          'substate': {'mysubstate_21': {'opstate': 'waiting', 'result': {}, 'config': {}, 'substate': {}}, \
                             'mysubstate_22': {'opstate': 'done', 'result': {}, 'config': {}, 'substate': {}}}}}}, shLoad1.toDict())
        shLoad2 = StateHandler()
        shLoad2.config = {'DEFAULT': {'statedir': '/tmp/test_cdmstatehandler'}}
        shLoad2.load()
        with self.subTest("set substates - load via config"):
            self.assertEqual({'opstate': 'uninitialized', 'result': {},
                              'config': {'DEFAULT': {'statedir':
                                                     '/tmp/test_cdmstatehandler'}},\
            'substate': {'mysubstate_1': {'opstate': 'uninitialized', 'result': {}, 'config': {}, 'substate': {}},\
                         'mysubstate_2': {'opstate': 'running', 'result': {}, 'config': {}, \
                                          'substate': {'mysubstate_21': {'opstate': 'waiting', 'result': {}, 'config': {}, 'substate': {}}, \
                             'mysubstate_22': {'opstate': 'done', 'result': {}, 'config': {}, 'substate': {}}}}}}, shLoad2.toDict())
        with self.subTest("delete via config - before"):
            self.assertTrue(os.path.isfile('/tmp/test_cdmstatehandler/state.json'))
        sh.delete()
        with self.subTest("delete via config - after"):
            self.assertFalse(os.path.isfile('/tmp/test_cdmstatehandler/state.json'))
        with self.subTest("delete direct - before"):
            self.assertTrue(os.path.isfile('/tmp/test_cdmstatehandler_2/state2.json'))
        sh.delete('/tmp/test_cdmstatehandler_2/state2.json')
        with self.subTest("delete direct - after"):
            self.assertFalse(os.path.isfile('/tmp/test_cdmstatehandler_2/state2.json'))
