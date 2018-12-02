#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from simpleloggerplus import simpleloggerplus as log
from subprocess import check_output, CalledProcessError
from cryptdomainmgr.modules.common.cdmstatehelper import isReady

def prepare(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

def rollover(serviceConfig, serviceState, state):
    serviceState.setOpStateWaiting()
    if not isReady(serviceConfig, state, ['dhparam', 'cert']):
        return
    serviceState.setOpStateRunning()
    log.info('  -> Apache2 reload')
    try:
        rv = check_output(('systemctl', 'start', 'apache2'))
        rv = check_output(('systemctl', 'reload', 'apache2'))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

    
