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
    if not isReady(serviceConfig, state, ['cert', 'dhparam']):
        return
    serviceState.setOpStateRunning()
    log.info('  -> Postfix reload')
    try:
        rv = check_output(('systemctl', 'start', 'postfix'))
        rv = check_output(('systemctl', 'reload', 'postfix'))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()


