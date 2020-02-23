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
    if not isReady(serviceConfig, state, 'dkim'):
        return
    serviceState.setOpStateRunning()
    log.info('  -> Rspamd reload')
    try:
        rv = check_output(('systemctl', 'start', 'rspamd'))
        #rv = check_output(('systemctl', 'reload', 'rspamd')) # this is not working with rspamd
        #rv = check_output(('rspamadm', 'control', 'reload'))
        # only restart works - bug in rspamd
        rv = check_output(('systemctl', 'restart', 'rspamd'))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

