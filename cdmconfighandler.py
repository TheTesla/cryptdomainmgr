#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import configparser

from simplelogger import simplelogger as log


def filterEntries(content, rrType):
    return {k: v for k, v in content.items() if rrType in k}

def splitList(content):
    return {k: e.strip() for k, v in content.items() for e in v.split(',')}

def parseNestedEntry(key, value, default = []):
    keyList   = key.split('.')
    valueList = value.split(':')
    addList   = list(default)
    rv = {}
    if '+' == keyList[-1][-1]:
        keyList[-1] = keyList[-1][:-1]
    else:
        rv['delList'] = list(keyList)
    addList[:len(keyList)] = list(keyList)
    for i, e in enumerate(valueList):
        addList[-i] = e
    rv['addList'] = addList
    return rv 

def list2dict(entry, hasContent, keys):
    entry.extend(['*'] * (len(keys) - len(entry)))
    rv = {e: entry[i] for i, e in enumerate(keys)}
    rv = {k: v for k, v in rv.items() if '*' != v}
    if hasContent is False:
        if keys[0] in rv:
            del rv[keys[0]]
    return rv

def list2SRV(srvEntry, hasContent = True):
    return list2dict(srvEntry, hasContent, ['server', 'service', 'proto', 'port', 'weight', 'prio'])

def list2MX(mxEntry, hasContent = True):
    return list2dict(mxEntry, hasContent, ['content', 'prio'])

def list2rrType(rrType, entry, hasContent = True):
    if 'mx' == rrType:
        return list2MX(entry, hasContent)
    elif 'srv' == rrType:
        return list2SRV(entry, hasContent)
    log.error('rrType not supported')

def interpreteRR(content, rrType = 'mx', defaultList = ['*', '10']):
    conf = splitList(filterEntries(content, rrType))
    parsedList = [parseNestedEntry(k, v, defaultList) for k, v in conf.items()]
    aggrAdd = [list2rrType(rrType, e['addList']) for e in parsedList]
    aggrDel = [list2rrType(rrType, e['delList'], False) for e in parsedList if 'delList' in e]
    return {'{}AggrAdd'.format(rrType): aggrAdd, '{}AggrDel'.format(rrType): aggrDel}

def interpreteMX(content):
    return interpreteRR(content, 'mx', ['*', '10'])

def interpreteSRV(content):
    return interpreteRR(content, 'srv', ['*', '*', '*', '*', '50', '10'])

class ConfigReader:
    def __init__(self):
        self.cp = configparser.ConfigParser()
        self.filenameList = []
        self.domainconfig = {}
        self.certconfig = {}
        self.dkimconfig = {}
        self.conflictingservices = {}

    def setFilenames(self, filenames):
        if filenames is None:
            return
        if type(filenames) is str:
            filenames = [filenames]
        self.filenameList = filenames

    def addFilenames(self, filenames):
        if filenames is None:
            return
        if type(filenames) is str:
            filenames = [filenames]
        self.filenameList.extend(filenames)

    def open(self):
        self.cp = configparser.ConfigParser()
        self.cp.read(self.filenameList)

    def interprete(self):
        self.domainconfig = interpreteDomainConfig(self.cp)
        self.certconfig = interpreteCertConfig(self.cp)
        self.dkimconfig = interpreteDKIMConfig(self.cp)
        self.conflictingservices = getConflictingServices(self.certconfig)


def interpreteDomainConfig(cf):
    domainconfig = getConfigOf('domain', cf, True)
    domainconfig = applyDefault(domainconfig) # must be here because following section depends on default values

    for domain, content in domainconfig.items():
        if 'ip4' in content.keys():
            domainconfig[domain]['ip4'] = domainconfig[domain]['ip4'].replace(' ', '').split(',')
        if 'ip4+' in content.keys():
            domainconfig[domain]['ip4+'] = domainconfig[domain]['ip4+'].replace(' ', '').split(',')
        if 'ip6' in content.keys():
            domainconfig[domain]['ip6'] = domainconfig[domain]['ip6'].replace(' ', '').split(',')
        if 'ip6+' in content.keys():
            domainconfig[domain]['ip6+'] = domainconfig[domain]['ip6+'].replace(' ', '').split(',')

        if 'mx' in [k.split('.')[0] for k in content.keys()]:
            mx = interpreteMX(content)
            log.debug(mx)
            domainconfig[domain].update(mx)

        if 'tlsa' in content:
            tlsa = str(domainconfig[domain]['tlsa'])
            if 'auto' == tlsa:
                tlsa = [[3, 0, 1], [3, 0, 2], [3, 1, 1], [3, 1, 2], [2, 0, 1], [2, 0, 2], [2, 1, 1], [2, 1, 2]]
            else:
                tlsa = [[int(f) for f in e] for e in tlsa.replace(' ', '').split(',')]
            domainconfig[domain]['tlsa'] = tlsa
        if 'spf' in content:
            domainconfig[domain]['spf'] = domainconfig[domain]['spf'].replace(' ', '').split(',')
        if 'spf+' in content:
            domainconfig[domain]['spf+'] = domainconfig[domain]['spf+'].replace(' ', '').split(',')
        if 'dmarc' in [k.split('.')[0] for k in content.keys()]:
            dmarc = {k.split('.')[1]: v for k, v in content.items() if 'dmarc' == k.split('.')[0]}
            domainconfig[domain]['dmarc'] = dmarc
        if 'srv' in [k.split('.')[0] for k in content.keys()]:
            srv = interpreteSRV(content)
            domainconfig[domain].update(srv)
        if 'soa' in [k.split('.')[0] for k in content.keys()]:
            domainconfig[domain]['soa'] = {k.split('.')[1]: v for k, v in content.items() if 'soa' == k.split('.')[0]}
        if 'caa' in content:
            domainconfig[domain]['caa'] = [(lambda x: {'flag': x[0], 'tag': x[1], 'url': x[2]})([f for f in e.split(' ') if '' != f]) for e in domainconfig[domain]['caa'].split(',')]
        if 'caa+' in content:
            domainconfig[domain]['caa+'] = [(lambda x: {'flag': x[0], 'tag': x[1], 'url': x[2]})([f for f in e.split(' ') if '' != f]) for e in domainconfig[domain]['caa+'].split(',')]

    log.debug(domainconfig)
    return domainconfig

def interpreteDKIMConfig(cf):
    defaultDKIMConfig = {'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'signingconftemporaryfile': '/etc/rspamd/dkim_signing_new.conf', 'signingconftemplatefile': '/etc/rspamd/local.d/dkim_signing.conf'}
    dkimconfig = getConfigOf('dkim', cf)
    # apply general config defaults and the default section
    dkimconfig = applyDefault(dkimconfig, defaultDKIMConfig) # must be here because following section depends on default values
    return dkimconfig

def interpreteCertConfig(cf):
    defaultCertConfig = {'source': '/etc/letsencrypt/live', 'certname': 'fullchain.pem', 'keysize': 4096, 'extraflags': ''}
    certconfig = getConfigOf('certificate', cf)
    # apply general config defaults and the default section
    certconfig = applyDefault(certconfig, defaultCertConfig) # must be here because following section depends on default values



    for certSecName, content in certconfig.items():
        if 'generator' in content:
            log.debug('generator in content')
            if 'certbot' == str(content['generator']): # certbot default certificate location - overrides source config
                log.debug('certbot is generator')
                certconfig[certSecName]['source'] = '/etc/letsencrypt/live'
        if 'keysize' in content:
            certconfig[certSecName]['keysize'] = int(certconfig[certSecName]['keysize'])
        if 'extraflags' in content:
            certconfig[certSecName]['extraflags'] = content['extraflags'].replace(' ', '').split(',')
        if 'conflictingservices' in content:
            conflictingservices = content['conflictingservices'].replace(' ', '').split(',')
            if '' == conflictingservices[0]:
                conflictingservices = []
            certconfig[certSecName]['conflictingservices'] = conflictingservices
    log.debug(certconfig)
    return certconfig


def applyDefault(config, defaultConfig={}):
    default = dict(defaultConfig)
    if 'DEFAULT' in config:
        default.update(config['DEFAULT'])
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig

def getConflictingServices(certConfig):
    return {f for e in certConfig.values() if 'conflictingservices' in e for f in e['conflictingservices']}

def getConfigOf(getSection, config, domainOldStyle=False):
    resConfig = {}
    for name, content in config.items():
        section = name.split(':')
        if getSection != section[0]:
            if domainOldStyle is True:
                if '.' not in section[0]: # fallback if not domain:example.de but example.de
                    continue
            else:
                continue
        if 2 == len(section):
            secName = section[1]
        else:
            secName = 'DEFAULT'
            if domainOldStyle is True:
                if '.' in section[0]:
                    secName = section[0] # fallback if not domain:example.de but example.de
        resConfig[secName] = dict({str(k): str(v) for k, v in content.items()})
    return resConfig

