#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.cdmconfighandler import ConfigReader
from cryptdomainmgr.cdmstatehandler import StateHandler
#from cryptdomainmgr.modules.common.cdmconfighelper import getStateDir
from simpleloggerplus import simpleloggerplus as log

def getNextPhase(currentPhase):
    if 'prepare' == currentPhase:
        return 'rollover'
    if 'rollover' == currentPhase:
        return 'cleanup'
    return 'prepare'

def getCurrentPhase(state, forcePhase='next'):
    if 'next' != str(forcePhase):
        return forcePhase
    if 'nextphase' in state.result:
        return state.result['nextphase']
    return 'prepare'

# maybe ToDo: readConfig() -> addConfig() + setConfig()
# run() with explicit parameter to overwrite config
# option to mix config files and config content in the priority list
# INFO about config files and content read
class ManagedDomain:
    def __init__(self):
        self.cr = ConfigReader()
        self.sh = StateHandler()

    def readConfig(self, confFiles=[], confContent=''):
        self.cr.setFilenames(confFiles)
        self.cr.setContentList(confContent)
        self.cr.open()
        if 'cdm' not in self.cr.cp:
            self.cr.cp['cdm'] = {}
        self.cr.interprete(self.sh)
        self.sh.registerConfig(self.cr.config['cdm'])

    def run(self, confFile=None, forcePhase='next', confContent=''):
        if confFile is not None or 0 < len(confContent):
            self.readConfig(confFile, confContent)
        self.sh.load()
        self.sh.delete() # --next starts with prepare, if failed
        self.sh.resetOpStateRecursive()
        currentPhase = getCurrentPhase(self.sh, forcePhase)
        log.info('Running phase: {}'.format(currentPhase))
        runPhase(self.cr, self.sh, currentPhase)
        nextphase = getNextPhase(currentPhase)
        self.sh.registerResult({'nextphase': nextphase})
        self.sh.save()


def runPhase(cr, sh, phase):
    sh.setOpStateRunning()
    handler = {secName: __import__('cryptdomainmgr.modules.'+str(secName)+'.main', fromlist=('cryptdomainmgr','modules')) for secName in cr.sections}
    for i in range(10):
        for k, v in handler.items():
            if not hasattr(v, phase):
                continue
            f = getattr(v, phase)
            f(cr.config, sh)
    sh.setOpStateDone()





