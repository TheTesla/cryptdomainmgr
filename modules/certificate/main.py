#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from OpenSSL import crypto
import os
import handlercertbot as certmodule
import handlerdehydrated as certmodulenew
from subprocess import check_output
from simpleloggerplus import simpleloggerplus as log


def prepare(config, state, i=2):
    if i != 2:
        return
    log.info('Certificate prepare')
    subState = state.getSubstate('cert')
    for certSecName, certConfig in config['cert'].items():
        if 'DEFAULT' == certSecName:
            continue
        log.info('Create certificate for section \"{}\"'.format(certSecName))
        if 'handler' not in certConfig:
            continue
        certState = subState.getSubstate(certSecName)
        domains = [k for k,v in config['domain'].items() if 'certificate' in v and certSecName == v['certificate']]
        log.info('  -> {}'.format(', '.join(domains)))
        log.debug(certConfig)
        certmodule.prepare(certConfig, certState, domains, i) 
        certmodulenew.prepare(certConfig, certState, domains, i) 

def rollover(config, state, i=2):
    if i != 2:
        return
    log.info('Certificate rollover')
    subState = state.getSubstate('cert')
    for certSecName, certConfig in config['cert'].items():
        if 'DEFAULT' == certSecName:
            continue
        log.info('Create certificate for section \"{}\"'.format(certSecName))
        if 'handler' not in certConfig:
            continue
        certState = subState.getSubstate(certSecName)
        copyCert(certConfig, certState)

def cleanup(config, state, i=2):
    if i != 2:
        return
    log.info('Certificate cleanup')
    subState = state.getSubstate('cert')
    for certSecName, certConfig in config['cert'].items():
        if 'DEFAULT' == certSecName:
            continue
        log.info('Create certificate for section \"{}\"'.format(certSecName))
        if 'handler' not in certConfig:
            continue
        certState = subState.getSubstate(certSecName)
        certState.setOpStateUninitialized()

def copyCert(certConfig, certState):
    src = os.path.dirname(certState.result['fullchainfile'])
    for name in certState.result['san']:
        dest = os.path.join(certConfig['destination'], name)
        log.info('  {} -> {}'.format(src, dest))
        rv = check_output(('cp', '-rfLT', str(src), str(dest)))


#def findCertHelper(path, curName = None, nameList = [], filename = 'fullchain.pem', cert = None):
#    if path is None:
#        return None
#    path = os.path.expanduser(path)
#    if cert is not None:
#        cert = os.path.expanduser(cert)
#        certPath = cert
#        if True == os.path.isfile(certPath):
#            return certPath
#    if curName is not None:
#        certPath = os.path.join(path, curName, filename)
#        if True == os.path.isfile(certPath):
#            return certPath
#    certPath = path
#    if True == os.path.isfile(certPath):
#        return certPath
#    certPath = os.path.join(path, filename)
#    if True == os.path.isfile(certPath):
#        return certPath
#    for name in nameList:
#        certPath = os.path.join(path, name, filename)
#        if True == os.path.isfile(certPath):
#            return certPath
#    return ''
#    
#def findCert(name, content, config):
#    log.debug(config['cert'])
#    try:
#        certlocation = config['cert'][content['certificate']]['source']
#    except:
#        certlocation = None
#    if 'certificate' in content:
#        certSecName = content['certificate']
#    else:
#        certSecName = 'DEFAULT'
#    domainsOfSameCert = [k for k,v in config['domain'].items() if 'certificate' in v and certSecName == v['certificate']]
#    log.debug('  domainsOfSameCert = ' + str(domainsOfSameCert))
#    log.debug('  certlocation = %s' % certlocation)
#    log.debug('  name = ' +str(name))
#    if certSecName in config['cert']:
#        certName = config['cert'][certSecName]['certname']
#    else:
#        certName = 'fullchain.pem'
#    log.debug('  certname = ' +str(certName))
#    cert = findCertHelper(certlocation, name, domainsOfSameCert, certName, certlocation)
#    log.debug('  findCert = %s' % cert)
#    return cert

