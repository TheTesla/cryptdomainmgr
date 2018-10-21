#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from . import handlerapache2
from . import handlerrspamd
from . import handlerdovecot
from . import handlerpostfix

from simpleloggerplus import simpleloggerplus as log

def prepare(config, state):
    subState = state.getSubstate('service')
    for serviceSecName, serviceConfig in config['service'].items():
        if 'DEFAULT' == serviceSecName:
            continue
        serviceState = subState.getSubstate(serviceSecName)
        if serviceState.isDone():
            continue
        log.info('Prepare service for section \"{}\"'.format(serviceSecName))
        log.debug(serviceConfig)
        handler = __import__('modules.service.handler'+str(serviceSecName), fromlist=('modules','service'))
        resolveAuto(serviceConfig, config, ['cert', 'dkim'])
        handler.prepare(serviceConfig, serviceState, state) 

def rollover(config, state):
    subState = state.getSubstate('service')
    for serviceSecName, serviceConfig in config['service'].items():
        if 'DEFAULT' == serviceSecName:
            continue
        serviceState = subState.getSubstate(serviceSecName)
        if serviceState.isDone():
            continue
        log.info('Rollover service for section \"{}\"'.format(serviceSecName))
        log.debug(serviceConfig)
        handler = __import__('modules.service.handler'+str(serviceSecName), fromlist=('modules','service'))
        resolveAuto(serviceConfig, config, ['cert', 'dkim'])
        handler.rollover(serviceConfig, serviceState, state) 

def cleanup(config, state):
    subState = state.getSubstate('service')
    for serviceSecName, serviceConfig in config['service'].items():
        if 'DEFAULT' == serviceSecName:
            continue
        serviceState = subState.getSubstate(serviceSecName)
        if serviceState.isDone():
            continue
        log.info('Cleanup service for section \"{}\"'.format(serviceSecName))
        log.debug(serviceConfig)
        handler = __import__('modules.service.handler'+str(serviceSecName), fromlist=('modules','service'))
        resolveAuto(serviceConfig, config, ['cert', 'dkim'])
        handler.cleanup(serviceConfig, serviceState, state) 

def autoSec(secList, config, section):
    if 'auto' in secList:
       return [secName for secName, content in config[section].items() if 'DEFAULT' != secName]
    return secList

def resolveAuto(serviceConfig, config, depends):
    for e in depends:
        if e not in config:
            continue
        serviceConfig[e] = autoSec(serviceConfig[e], config, e)

