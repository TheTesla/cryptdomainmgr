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
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        if domainState.isDone():
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        log.debug(domainConfig)
        caaAuto(domainConfig, config)
        domainmodule.update(domainConfig, domainState, domainSecName) 


def prepare(config, state):
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        if domainState.isDone():
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        log.debug(domainConfig)
        domainmodule.prepare(domainConfig, domainState, domainSecName, state) 

def rollover(config, state):
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        if domainState.isDone():
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        domainmodule.rollover(domainConfig, domainState, domainSecName, state) 

def cleanup(config, state):
    subState = state.getSubstate('domain')
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        if 'handler' not in domainConfig:
            continue
        domainState = subState.getSubstate(domainSecName)
        if domainState.isDone():
            continue
        log.info('Create resource records for section \"{}\"'.format(domainSecName))
        domainmodule.cleanup(domainConfig, domainState, domainSecName, state) 


def caaAuto(domainConfig, config):
    if 'caa' not in domainConfig:
        return
    if 'auto' not in domainConfig['caa']:
        return
    domainConfig['caaAggrAdd'] = [e if e['flag'] != 'auto' else config['cert'][domainConfig['cert']]['caa'] for e in domainConfig['caaAggrAdd']]

