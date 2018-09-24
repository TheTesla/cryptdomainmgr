#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from OpenSSL import crypto
import os
#import handlercertbot as certmodule
import handlerdehydrated as certmodulenew
from subprocess import check_output
from simpleloggerplus import simpleloggerplus as log


def prepare(config, state):
    subState = state.getSubstate('cert')
    for certSecName, certConfig in config['cert'].items():
        if 'DEFAULT' == certSecName:
            continue
        if 'handler' not in certConfig:
            continue
        certState = subState.getSubstate(certSecName)
        if certState.isDone():
            continue
        domains = [k for k,v in config['domain'].items() if 'cert' in v and certSecName == v['cert']]
        log.info('Create certificate for section \"{}\"'.format(certSecName))
        log.info('  -> {}'.format(', '.join(domains)))
        log.debug(certConfig)
        certmodulenew.prepare(certConfig, certState, domains) 

def rollover(config, state):
    subState = state.getSubstate('cert')
    for certSecName, certConfig in config['cert'].items():
        if 'DEFAULT' == certSecName:
            continue
        if 'handler' not in certConfig:
            continue
        certState = subState.getSubstate(certSecName)
        if certState.isDone():
            continue
        log.info('Apply certificate for section \"{}\"'.format(certSecName))
        copyCert(certConfig, certState)
        certState.setOpStateDone()

def cleanup(config, state):
    subState = state.getSubstate('cert')
    for certSecName, certConfig in config['cert'].items():
        if 'DEFAULT' == certSecName:
            continue
        if 'handler' not in certConfig:
            continue
        certState = subState.getSubstate(certSecName)
        if certState.isDone():
            continue
        log.info('Cleanup certificate for section \"{}\"'.format(certSecName))
        certState.setOpStateDone()
        #certState.setOpStateUninitialized()

def copyCert(certConfig, certState):
    src = os.path.dirname(certState.result['fullchainfile'])
    for name in certState.result['san']:
        dest = os.path.join(certConfig['destination'], name)
        log.info('  {} -> {}'.format(src, dest))
        rv = check_output(('cp', '-rfLT', str(src), str(dest)))

