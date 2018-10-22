#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from OpenSSL import crypto
import os
from subprocess import check_output
from simpleloggerplus import simpleloggerplus as log


def createDomainAccessTable(config, domains):
    domainAccessTableStr = ""
    for d in domains:
        domainConfig = config['domain'][d]
        paramKeys = domainConfig['accessparams']
        domainAccessTableStr += ' ["{}"]="'.format(d) + '\\n'.join(["{}={}".format(k, domainConfig[k]) for k in paramKeys])+'"'
    return '({} )'.format(domainAccessTableStr)


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
        domainAccessTable = createDomainAccessTable(config, domains)
        handlerNames = certConfig['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.cert.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr', 'modules','cert'))
        handler.prepare(certConfig, certState, domains, domainAccessTable) 

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
        delOldCert(certConfig, certState)
        certState.setOpStateDone()

def copyCert(certConfig, certState):
    src = os.path.dirname(certState.result['fullchainfile'])
    for name in certState.result['san']:
        dest = os.path.join(certConfig['destination'], name)
        log.info('  {} -> {}'.format(src, dest))
        rv = check_output(('cp', '-rfLT', str(src), str(dest)))

def delOldCert(certConfig, certState):
    preserve = ['fullchainfile', 'certfile', 'keyfile', 'chainfile']
    preserveFiles = set([certState.result[e] for e in preserve])
    preserveFiles.update(set([os.path.realpath(e) for e in preserveFiles]))
    dirs = set([os.path.dirname(e) for e in preserveFiles])
    dirs = [e for e in dirs if os.path.isdir(e)]
    allFiles = set([os.path.join(d, f) for d in dirs for f in os.listdir(d)])
    allFiles = set([e for e in allFiles if os.path.isfile(e)])
    removeFiles = allFiles - preserveFiles
    for e in removeFiles:
        log.info('  rm {}'.format(e))
        rv = check_output(('rm', str(e)))







