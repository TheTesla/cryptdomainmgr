#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cdmconfighandler import *
from cdmstatehandler import *
from simpleloggerplus import simpleloggerplus as log

class ManagedDomain:
    def __init__(self):
        self.cr = ConfigReader()
        self.sh = StateHandler()

    def readConfig(self, confFiles):
        self.cr.setFilenames(confFiles)
        self.cr.open()
        self.cr.interprete(self.sh)


    def update(self, state = '', confFile = None):
        self.readConfig(confFile)
        runPhase(self.cr, self.sh, 'update')

    def prepare(self, confFile = None):
        self.readConfig(confFile)
        runPhase(self.cr, self.sh, 'prepare')
        self.sh.save()

    def rollover(self, confFile = None):
        self.sh.load()
        self.sh.resetOpStateRecursive()
        self.readConfig(confFile)
        runPhase(self.cr, self.sh, 'rollover')
        self.sh.save()

    def cleanup(self, confFile = None):
        self.sh.load()
        self.sh.resetOpStateRecursive()
        self.readConfig(confFile)
        runPhase(self.cr, self.sh, 'cleanup')
        self.sh.save()


def runPhase(cr, sh, phase):
    handler = {secName: __import__('modules.'+str(secName)+'.main', fromlist=('modules')) for secName in cr.sections}
    for i in range(10):
        for k, v in handler.items():
            if not hasattr(v, phase):
                continue
            f = getattr(v, phase)
            f(cr.config, sh)





