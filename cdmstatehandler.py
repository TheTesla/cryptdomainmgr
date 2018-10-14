#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import json
import os
from modules.common.cdmfilehelper import makeDir

class StateHandler:
    def __init__(self):
        self.opstate = ''
        self.result = {}
        self.config = {}
        self.substate = {}
        self.setOpStateUninitialized()

    def setOpState(self, opState):
        self.opstate = str(opState)

    def resetOpStateRecursive(self):
        self.setOpStateUninitialized()
        for k, v in self.substate.items():
            v.resetOpStateRecursive()

    # initial state
    def setOpStateUninitialized(self):
        self.setOpState("uninitialized")

    # waiting for results produced by other modules/handlers
    def setOpStateWaiting(self):
        self.setOpState("waiting")

    # module/handler is doing work
    def setOpStateRunning(self):
        self.setOpState("running")

    # module/handler is ready, results are written
    def setOpStateDone(self):
        self.setOpState("done")

    def isDone(self):
        return 'done' == self.opstate

    def isSubDone(self):
        return 0 == len([0 for k, v in self.substate.items() if not v.isDone()])


    # should be the output after handler/module run is done
    # example: certificate source = /etc/dehydrated/certs/exampel.domain
    def registerResult(self, result):
        self.result = result

    # should be the output known before module run
    # exmaple: certificate = letsencrypt -> CAA[auto] = letsencrypt
    def registerConfig(self, config): 
        self.config = config

    def registerSubstate(self, sectionName):
        if str(sectionName) not in self.substate:
            self.substate[str(sectionName)] = StateHandler()

    def getSubstate(self, sectionName):
        self.registerSubstate(sectionName)
        return self.substate[str(sectionName)]

    def printAll(self, indent=0):
        print('{} opstate = {}'.format(indent * ' ', self.opstate))
        print('{} result  = {}'.format(indent * ' ', self.result))
        print('{} config  = {}'.format(indent * ' ', self.config))
        for k, v in self.substate.items():
            print('{} substate = {}'.format(indent * ' ', k))
            v.printAll(indent+1)

    def toDict(self):
        return {'opstate': self.opstate, 'result': self.result, 'config': self.config, 'substate': {k: v.toDict() for k, v in self.substate.items()}}
                
    def fromDict(self, stateDict):
        self.opstate = stateDict['opstate']
        self.result = stateDict['result']
        self.config = stateDict['config']
        for k, v in stateDict['substate'].items():
            self.substate[k] = StateHandler()
            self.substate[k].fromDict(v)

    def save(self, filename=None):
        if filename is None:
            filename = os.path.join(self.config['statedir'], 'state.json')
        makeDir(os.path.dirname(filename))
        with open(filename, 'w') as jsonfile:
            json.dump(self.toDict(), jsonfile)

    def delete(self, filename=None):
        if filename is None:
            filename = os.path.join(self.config['statedir'], 'state.json')
        if not os.path.isfile(filename):
            return
        os.remove(filename)

    def load(self, filename=None):
        if filename is None:
            filename = os.path.join(self.config['statedir'], 'state.json')
        if not os.path.isfile(filename):
            return
        with open(filename, 'r') as jsonfile:
            self.fromDict(json.load(jsonfile))


