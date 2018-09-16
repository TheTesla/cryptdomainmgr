#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

class StateHandler:
    def __init__(self):
        self.state = {}
        self.opstate = ''
        self.result = {}
        self.config = {}
        self.substate = {}
        self.setOpStateUninitialized()

    def setOpState(self, opState):
        self.opstate = str(opState)

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

                



