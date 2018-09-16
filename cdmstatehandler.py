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

    def initPart(self, partName):
        if str(partName) not in self.state:
            self.state[str(partName)] = {}

    def initSection(self, partName, sectionName):
        self.initPart(partName)
        if str(sectionName) not in self.state[str(partName)]:
            self.state[str(partName)][str(sectionName)] = {}
            self.setOpStateUninitialized(partName, sectionName)

    def setOpState(self, partName, sectionName, opState):
        self.state[str(partName)][str(sectionName)]["opstate"] = str(opState)

    def setOpStateUninitialized(self, partName, sectionName):
        self.setOpState(partName, sectionName, "uninitialized")

    def setOpStateWaiting(self, partName, sectionName):
        self.setOpState(partName, sectionName, "waiting")

    def setOpStateRunning(self, partName, sectionName):
        self.setOpState(partName, sectionName, "running")

    def setOpStateDone(self, partName, sectionName):
        self.setOpState(partName, sectionName, "done")

    # should be the output after handler/module run is done
    # example: certificate source = /etc/dehydrated/certs/exampel.domain
    def registerResult(self, partName, sectionName, result):
        self.state[str(partName)][str(sectionName)]['result'] = result

    # should be the output known before module run
    # exmaple: certificate = letsencrypt -> CAA[auto] = letsencrypt
    def regsiterConfig((self, partName, sectionName, config): 
        self.state[str(partName)][str(sectionName)]['config'] = config

