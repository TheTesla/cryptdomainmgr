#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from simpleloggerplus import simpleloggerplus as log
from subprocess import check_output

def prepare(serviceConfig, serviceState, serviceSecName, state):
    serviceState.setOpStateDone()

def rollover(serviceConfig, serviceState, serviceSecName, state):
    serviceState.setOpStateWaiting()
    if not isReady(serviceConfig, state, 'cert'):
        return
    serviceState.setOpStateRunning()
    log.info('  -> Dovecot reload')
    rv = check_output(('systemctl', 'reload', 'dovecot'))
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, serviceSecName, state):
    serviceState.setOpStateDone()


def isReady(serviceConfig, state, sec):
    subState = state.getSubstate(sec)
    return 0 == len([0 for e in serviceConfig[sec] if not subState.getSubstate(e).isDone()])
    
