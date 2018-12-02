#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from OpenSSL import crypto
import os
from subprocess import check_output, CalledProcessError
from simpleloggerplus import simpleloggerplus as log
from cryptdomainmgr.modules.common.cdmconfighelper import getStateDir

def prepare(config, state):
    subState = state.getSubstate('dhparam')
    for dhparamSecName, dhparamConfig in config['dhparam'].items():
        if 'DEFAULT' == dhparamSecName:
            continue
        if 'handler' not in dhparamConfig:
            continue
        dhparamState = subState.getSubstate(dhparamSecName)
        if dhparamState.isDone():
            continue
        log.info('Create dhparams for section \"{}\"'.format(dhparamSecName))
        log.debug(dhparamConfig)
        handlerNames = dhparamConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.dhparam.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr', 'modules','dhparam'))
        statedir = getStateDir(config, 'dhparam', dhparamSecName)
        handler.prepare(dhparamConfig, dhparamState, statedir, dhparamSecName) 

def rollover(config, state):
    subState = state.getSubstate('dhparam')
    for dhparamSecName, dhparamConfig in config['dhparam'].items():
        if 'DEFAULT' == dhparamSecName:
            continue
        if 'handler' not in dhparamConfig:
            continue
        dhparamState = subState.getSubstate(dhparamSecName)
        if dhparamState.isDone():
            continue
        log.info('Apply dhparam for section \"{}\"'.format(dhparamSecName))
        copyDH(dhparamConfig, dhparamState)
        dhparamState.setOpStateDone()

def cleanup(config, state):
    subState = state.getSubstate('dhparam')
    for dhparamSecName, dhparamConfig in config['dhparam'].items():
        if 'DEFAULT' == dhparamSecName:
            continue
        if 'handler' not in dhparamConfig:
            continue
        dhparamState = subState.getSubstate(dhparamSecName)
        if dhparamState.isDone():
            continue
        log.info('Cleanup dhparam for section \"{}\"'.format(dhparamSecName))
        dhparamState.setOpStateDone()

def copyDH(dhparamConfig, dhparamState):
    if 'tmpfile' not in dhparamState.result:
        return 
    src = os.path.realpath(dhparamState.result['tmpfile'])
    dest = os.path.realpath(dhparamConfig['filename'])
    try:
        os.makedirs(os.path.dirname(dest))
    except:
        pass
    log.info('  {} -> {}'.format(src, dest))
    try:
        rv = check_output(('cp', '-rfLT', str(src), str(dest)))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)







