#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from simpleloggerplus import simpleloggerplus as log
from subprocess import check_output, CalledProcessError

def prepare(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

def rollover(serviceConfig, serviceState, state):
    serviceState.setOpStateWaiting()
    if not isReady(serviceConfig, state, 'cert'):
        return
    serviceState.setOpStateRunning()
    log.info('  -> Dovecot reload')
    try:
        rv = check_output(('systemctl', 'reload', 'dovecot'))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()


def isReady(serviceConfig, state, sec):
    subState = state.getSubstate(sec)
    return 0 == len([0 for e in serviceConfig[sec] if not subState.getSubstate(e).isDone()])
    
