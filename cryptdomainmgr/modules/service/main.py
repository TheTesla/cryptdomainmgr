#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from simpleloggerplus import simpleloggerplus as log

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
        handler.prepare(serviceConfig, serviceState, state)

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
        handler.rollover(serviceConfig, serviceState, state)

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
        handler.cleanup(serviceConfig, serviceState, state)


