#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import inspect
from simpleloggerplus import simpleloggerplus as log

# handlers may accept an optional 4th argument with the complete config
# (needed by e.g. handleropendkim to resolve the domain references of a
# dkim section); old 3-argument handlers keep working
def callHandler(handler, phaseName, config, serviceConfig, serviceState, state):
    args = [serviceConfig, serviceState, state]
    if 3 < len(inspect.signature(getattr(handler, phaseName)).parameters):
        args.append(config)
    getattr(handler, phaseName)(*args)

def prepare(config, state):
    subState = state.getSubstate('service')
    for serviceSecName, serviceConfig in config['service'].items():
        if 'DEFAULT' == serviceSecName:
            continue
        if 'handler' not in serviceConfig:
            continue
        serviceState = subState.getSubstate(serviceSecName)
        if serviceState.isDone():
            continue
        log.info('Prepare service for section \"{}\"'.format(serviceSecName))
        log.debug(serviceConfig)
        handlerNames = serviceConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.service.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr', 'modules','service'))
        callHandler(handler, 'prepare', config, serviceConfig, serviceState, state)

def rollover(config, state):
    subState = state.getSubstate('service')
    for serviceSecName, serviceConfig in config['service'].items():
        if 'DEFAULT' == serviceSecName:
            continue
        if 'handler' not in serviceConfig:
            continue
        serviceState = subState.getSubstate(serviceSecName)
        if serviceState.isDone():
            continue
        log.info('Rollover service for section \"{}\"'.format(serviceSecName))
        log.debug(serviceConfig)
        handlerNames = serviceConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.service.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr', 'modules','service'))
        callHandler(handler, 'rollover', config, serviceConfig, serviceState, state)

def cleanup(config, state):
    subState = state.getSubstate('service')
    for serviceSecName, serviceConfig in config['service'].items():
        if 'DEFAULT' == serviceSecName:
            continue
        if 'handler' not in serviceConfig:
            continue
        serviceState = subState.getSubstate(serviceSecName)
        if serviceState.isDone():
            continue
        log.info('Cleanup service for section \"{}\"'.format(serviceSecName))
        log.debug(serviceConfig)
        handlerNames = serviceConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.service.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr', 'modules','service'))
        callHandler(handler, 'cleanup', config, serviceConfig, serviceState, state)
