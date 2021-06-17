#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2021 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


import time
from cryptdomainmgr.modules.common.cdmstatehelper import isReady
from simpleloggerplus import simpleloggerplus as log

def postwait(config, state):
    #print(config)
    subState = state.getSubstate('cdm')
    if subState.isDone():
        return
    for cdmSecName, cdmConfig in config['cdm'].items():
        cdmState = subState.getSubstate(cdmSecName)
        if cdmState.isDone():
            continue
        if not isReady(cdmConfig, state, ['dhparam', 'cert', 'domain', 'dkim',
                                         'service']):
        #if not isReady(cdmConfig, state, ['cert']):
            return
        if 'postwait' in cdmConfig:
            T = cdmConfig['postwait']
            log.info('Wait {} s after run!'.format(T))
            time.sleep(int(T))
    subState.setOpStateDone()

def prepare(config, state):
    postwait(config, state)

def rollover(config, state):
    postwait(config, state)

def cleanup(config, state):
    postwait(config, state)

