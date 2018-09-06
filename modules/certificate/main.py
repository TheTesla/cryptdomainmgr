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
from subprocess import check_output
from simpleloggerplus import simpleloggerplus as log


def certPrepare(config, i=2):
    if i != 2:
        return
    log.info('Certificate prepare')
    #self.stop80()
    createCert(config)
    #self.start80()

def certRollover(config, i=2):
    if i != 2:
        return
    log.info('Certificate rollover')
    copyCert(config)

def certCleanup(config, i=2):
    if i != 2:
        return
    log.info('Certificate cleanup')
        
def getCertSAN(filename):
    certFile = open(filename, 'rt').read()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certFile)
    san = [cert.get_extension(i).get_data().split('\x82')[1:] for i in range(cert.get_extension_count()) if 'subjectAltName' == cert.get_extension(i).get_short_name()][0]
    san = [e[1:] for e in san]
    return san

def findCertHelper(path, curName = None, nameList = [], filename = 'fullchain.pem', cert = None):
    if path is None:
        return None
    path = os.path.expanduser(path)
    if cert is not None:
        cert = os.path.expanduser(cert)
        certPath = cert
        if True == os.path.isfile(certPath):
            return certPath
    if curName is not None:
        certPath = os.path.join(path, curName, filename)
        if True == os.path.isfile(certPath):
            return certPath
    certPath = path
    if True == os.path.isfile(certPath):
        return certPath
    certPath = os.path.join(path, filename)
    if True == os.path.isfile(certPath):
        return certPath
    for name in nameList:
        certPath = os.path.join(path, name, filename)
        if True == os.path.isfile(certPath):
            return certPath
    return ''
    
def findCert(name, content, config):
    log.debug(config['cert'])
    try:
        certlocation = config['cert'][content['certificate']]['source']
    except:
        certlocation = None
    if 'certificate' in content:
        certSecName = content['certificate']
    else:
        certSecName = 'DEFAULT'
    domainsOfSameCert = [k for k,v in config['domain'].items() if 'certificate' in v and certSecName == v['certificate']]
    log.debug('  domainsOfSameCert = ' + str(domainsOfSameCert))
    log.debug('  certlocation = %s' % certlocation)
    log.debug('  name = ' +str(name))
    if certSecName in config['cert']:
        certName = config['cert'][certSecName]['certname']
    else:
        certName = 'fullchain.pem'
    log.debug('  certname = ' +str(certName))
    cert = findCertHelper(certlocation, name, domainsOfSameCert, certName, certlocation)
    log.debug('  findCert = %s' % cert)
    return cert

def createCert(config):
    for certSecName, certConfig in config['cert'].items():
        if 'handler' not in certConfig:
            continue
        log.info('Create certificate for section \"{}\"'.format(certSecName))
        domains = [k for k,v in config['domain'].items() if 'certificate' in v and certSecName == v['certificate']]
        log.info('  -> {}'.format(', '.join(domains)))
        log.debug(certConfig)
        certmodule.createCert(domains, certConfig) 


def copyCert(config):
    log.info('Copy certificate')
    for name, content in config['domain'].items():
        log.debug(name)
        if 'DEFAULT' == name:
            continue
        if 'certificate' not in content:
            continue
        src = os.path.dirname(findCert(name, content, config))
        dest = os.path.join(config['cert'][content['certificate']]['destination'], name)
        log.info('  {} -> {}'.format(src, dest))
        rv = check_output(('cp', '-rfLT', str(src), str(dest)))

