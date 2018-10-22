#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from simpleloggerplus import simpleloggerplus as log

def prepare(config, state):
    subState = state.getSubstate('dkim')
    for dkimSecName, dkimConfig in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        if 'handler' not in dkimConfig:
            continue
        dkimState = subState.getSubstate(dkimSecName)
        if dkimState.isDone():
            continue
        log.info("Preparing DKIM key for dkim-section: \"{}\"".format(dkimSecName))
        handlerNames = dkimConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.dkim.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr','modules','dkim'))
        handler.prepare(dkimConfig, dkimState)

def rollover(config, state):
    subState = state.getSubstate('dkim')
    for dkimSecName, dkimConfig in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        if 'handler' not in dkimConfig:
            continue
        dkimState = subState.getSubstate(dkimSecName)
        if dkimState.isDone():
            continue
        log.info("Applying DKIM key for dkim-section: \"{}\"".format(dkimSecName))
        handlerNames = dkimConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.dkim.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr','modules','dkim'))
        handler.rollover(dkimConfig, dkimState)

def cleanup(config, state):
    subState = state.getSubstate('dkim')
    for dkimSecName, dkimConfig in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        if 'handler' not in dkimConfig:
            continue
        dkimState = subState.getSubstate(dkimSecName)
        if dkimState.isDone():
            continue
        log.info("Cleanup DKIM key for dkim-section: \"{}\"".format(dkimSecName))
        handlerNames = dkimConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.dkim.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr','modules','dkim'))
        handler.cleanup(dkimConfig, dkimState)

