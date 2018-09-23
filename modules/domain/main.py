#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import handlerdnsuptools as domainmodule
from simpleloggerplus import simpleloggerplus as log


def update(config, state):
    log.info('Domain update')
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        log.debug(domainConfig)
        domainmodule.update(domainConfig, domainState, domainSecName) 


def prepare(config, state):
    log.info('Domain prepare')
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        log.debug(domainConfig)
        domainmodule.prepare(domainConfig, domainState, domainSecName, state) 

def rollover(config, state):
    log.info('Domain rollover')
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        domainmodule.rollover(domainConfig, domainState, domainSecName, state) 

def cleanup(config, state):
    log.info('Domain cleanup')
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        domainmodule.cleanup(domainConfig, domainState, domainSecName, state) 
        #domainState.setOpStateUninitialized()

