#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import configparser
import os
import re

def mxParse(mxStr, prioDefault = 10):
        mxPrio = mxStr.split(':')
        if 2 == len(mxPrio):
            return (str(mxPrio[0]), int(mxPrio[1]))
        elif 1 == len(mxPrio):
            return (str(mxPrio[0]), int(prioDefault))
        else:
            return ()

def parseBool(x):
    if type(x) is bool:
        return x
    else:
        x = str(x)
        x = re.sub(' ', '', x)
        x = x.lower()
        if 'true' == x:
            print(x)
            return True
        elif '1' == x:
            return True
        elif 'yes' == x:
            return True
        else:
            return False

def srvParseDel(srv):
    defaultAggrDel = {'content': [], 'prio': '*', 'key': []}
    for i, e in enumerate(srv['aggrDelList']):
        aggrDel = dict(defaultAggrDel)
        aggrDel.update(e)
        aggrDel['content'].extend(6*['*'])
        aggrDel['key'].extend(6*['*'])
        srv['aggrDelList'][i] = aggrDel
    print(srv['aggrDelList'])
    srvAggrDel = [{'prio': e['prio'], 'service': e['key'][1], 'proto': e['key'][2], 'port': e['key'][3], 'weight':  e['key'][4]} for e in srv['aggrDelList']] 
    srvAggrDel = [{k: v for k, v in e.items() if '*' != str(v)} for e in srvAggrDel]
    return srvAggrDel

def srvParseAdd(srv):
    defaultAggrAdd = {'content': [], 'prio': '*', 'key': []}
    for i, e in enumerate(srv['aggrAddList']):
        aggrAdd = dict(defaultAggrAdd)
        aggrAdd.update(e)
        aggrAdd['content'].extend(6*['*'])
        aggrAdd['key'].extend(6*['*'])
        srv['aggrAddList'][i] = aggrAdd
    srvAggrAddKey= [{'server': e['content'][0], 'prio': e['prio'], 'service': e['key'][1], 'proto': e['key'][2], 'port': e['key'][3], 'weight':  e['key'][4]} for e in srv['aggrAddList']] 
    srvAggrAddVal= [{'server': e['content'][0], 'prio': e['prio'], 'service': e['content'][5], 'proto': e['content'][4], 'port': e['content'][3], 'weight':  e['content'][2]} for e in srv['aggrAddList']] 
    for i, e in enumerate(srvAggrAddVal):
        srvAggrAddKey[i].update(e)
    srvAggrAdd = [{k: v for k, v in e.items() if '*' != str(v)} for e in srvAggrAddKey]
    return srvAggrAdd

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

def prioParse(content, rrType = 'mx', removeSpaces = True, dotsLeft = 0, keySplit = False, colonArgs = False):
    setList = []
    addList = []
    aggrAddList = []
    aggrDelList = []
    for k, v in content.items():
        if '+' == k[-1]:
            addMode = True
            k = k[:-1]
        else:
            addMode = False
        ks = k.rsplit('.', dotsLeft+1)
        if rrType != k.split('.')[0]:
            continue
        print(v)
        if removeSpaces is True:
            v = v.replace(' ', '')
        vList = v.split(',')
        for v in vList:
            vs = v.split(':')
            if keySplit is True:
                ks[0] = ks[0].split('.')
            if colonArgs is True:
                args = vs
            else:
                args = vs[0]
            item = {'content': args, 'key': ks[0], 'delprio': '*', 'addprio': 10}
            baseItem = {'content': args, 'key': ks[0]}
            delItem = dict(baseItem)
            addItem = dict(baseItem)
            addItem['prio'] = 10 # default
            if 2 == len(ks):
                item['delprio'] = ks[1]
                item['addprio'] = ks[1]
                delItem['prio'] = ks[1]
                addItem['prio'] = ks[1]
            if 2 <= len(vs):
                item['addprio'] = vs[1]
                addItem['prio'] = vs[1]
            if addMode is True:
                addList.append(item)
                aggrAddList.append(addItem)
            else:
                setList.append(item)
                aggrDelList.append(delItem)
    return {'addList': addList, 'setList': setList, 'aggrAddList':  aggrAddList, 'aggrDelList': aggrDelList}

def interpreteDomainConfig(cf):
    #domainconfig = {}
    #for name, content in cf.items():
    #    section = name.split(':')
    #    if 'domain' != section[0]:
    #        if '.' not in section[0]: # fallback if not domain:example.de but example.de
    #            continue
    #    if 2 == len(section):
    #        domain = section[1]
    #    else:
    #        domain = 'DEFAULT'
    #        if '.' in section[0]:
    #            domain = section[0] # fallback if not domain:example.de but example.de
    #    domainconfig[domain] = dict({str(k): str(v) for k, v in content.items()})
    domainconfig = getConfigOf('domain', cf, True)
    domainconfig = applyDefault(domainconfig) # must be here because following section depends on default values

    for domain, content in domainconfig.items():
        if 'ip4' in content.keys():
            domainconfig[domain]['ip4'] = domainconfig[domain]['ip4'].replace(' ','').split(',')
        if 'ip4+' in content.keys():
            domainconfig[domain]['ip4+'] = domainconfig[domain]['ip4+'].replace(' ','').split(',')
        if 'ip6' in content.keys():
            domainconfig[domain]['ip6'] = domainconfig[domain]['ip6'].replace(' ','').split(',')
        if 'ip6+' in content.keys():
            domainconfig[domain]['ip6+'] = domainconfig[domain]['ip6+'].replace(' ','').split(',')

        if 'mx' in [k.split('.')[0] for k in content.keys()]:    
            mx = prioParse(content)
            #mxSetList = []
            #mxAddList = []
            #for k, v in content.items():
            #    if '+' == k[-1]:
            #        addMode = True
            #        k = k[:-1]
            #    else:
            #        addMode = False
            #    ks = k.split('.')
            #    if 'mx' != ks[0]:
            #        continue
            #    print(v)
            #    vList = v.replace(' ', '').split(',')
            #    for v in vList:
            #        vs = v.split(':')
            #        mx = {'content': vs[0], 'delprio': '*', 'addprio': 10}
            #        if 2 == len(ks):
            #            mx['delprio'] = ks[1]
            #            mx['addprio'] = ks[1]
            #        if 2 == len(vs):
            #            mx['addprio'] = vs[1]
            #        if addMode is True:
            #            mxAddList.append(mx)
            #        else:
            #            mxSetList.append(mx)
            domainconfig[domain]['mxSet'] = mx['setList'] #mxSetList
            domainconfig[domain]['mxAdd'] = mx['addList'] #mxAddList
            domainconfig[domain]['mxAggrDel'] = mx['aggrDelList'] #mxSetList
            domainconfig[domain]['mxAggrAdd'] = mx['aggrAddList'] #mxAddList


        #if 'mx' in content.keys():
        #    mx = content['mx']
        #    mxList = mx.replace(' ', '').split(',')
        #    mxPrioList = [mxParse(e) for e in mxList]
        #    mxPrioDict = {e[0]: e[1] for e in mxPrioList}
        #    domainconfig[domain]['mx'] = dict(mxPrioDict)
        if 'tlsa' in content:
            tlsa = str(domainconfig[domain]['tlsa'])
            if 'auto' == tlsa:
                tlsa = [[3,0,1], [3,0,2], [3,1,1], [3,1,2], [2,0,1], [2,0,2], [2,1,1], [2,1,2]]
            else:
                tlsa = [[int(f) for f in e] for e in tlsa.replace(' ', '').split(',')]
            domainconfig[domain]['tlsa'] = tlsa
        if 'spf' in content:
            domainconfig[domain]['spf'] = domainconfig[domain]['spf'].replace(' ','').split(',')
        if 'spf+' in content:
            domainconfig[domain]['spf+'] = domainconfig[domain]['spf+'].replace(' ','').split(',')
        if 'dmarc' in [k.split('.')[0] for k in content.keys()]:
            dmarc = {k.split('.')[1]: v for k, v in content.items() if 'dmarc' == k.split('.')[0]}
            domainconfig[domain]['dmarc'] = dmarc
        if 'srv' in [k.split('.')[0] for k in content.keys()]:
            srv = prioParse(content, 'srv', True, 4, True, True)
            srvDel = srvParseDel(srv)
            srvAdd = srvParseAdd(srv)
            domainconfig[domain]['srvAggrAdd'] = srvAdd #[{'server': e['content'], 'prio': e['prio'], 'service:': e['key'][1], 'proto': e['key'][2], 'port': e['key'][3], 'weight':  k['key'][4]} for e in srv['aggrAddList']] 
            domainconfig[domain]['srvAggrDel'] = srvDel #[{'server': e['content'], 'prio': e['prio'], 'service:': e['key'][1], 'proto': e['key'][2], 'port': e['key'][3], 'weight':  k['key'][4]} for e in srv['aggrDelList']] 
            domainconfig[domain]['srv'] = [{'server': v.split(':')[0], 'prio': v.split(':')[1], 'service': k.split('.')[1], 'proto': k.split('.')[2], 'port': k.split('.')[3], 'weight':  k.split('.')[4]} for k, v in content.items() if 'srv' == k.split('.')[0]]
        if 'soa' in [k.split('.')[0] for k in content.keys()]:
            domainconfig[domain]['soa'] =  {k.split('.')[1]: v for k, v in content.items() if 'soa' == k.split('.')[0]}
        if 'caa' in content:
            domainconfig[domain]['caa'] = [(lambda x: {'flag': x[0], 'tag': x[1], 'url': x[2]})([f for f in e.split(' ') if '' != f]) for e in domainconfig[domain]['caa'].split(',')]
        if 'caa+' in content:
            domainconfig[domain]['caa+'] = [(lambda x: {'flag': x[0], 'tag': x[1], 'url': x[2]})([f for f in e.split(' ') if '' != f]) for e in domainconfig[domain]['caa+'].split(',')]

    print(domainconfig)    
    return domainconfig

def interpreteDKIMConfig(cf):
    defaultDKIMConfig = {'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'signingconftemplatefile': './dkim_signing_template.conf', 'signingconftemporaryfile': '/etc/rspamd/dkim_signing_new.conf', 'signingconftemplatefile': '/etc/rspamd/local.d/dkim_signing.conf'}
    #dkimconfig = {}
    #for name, content in cf.items():
    #    section = name.split(':')
    #    if 'dkim' != section[0]:
    #        continue
    #    if 2 == len(section):
    #        dkimSecName = section[1]
    #    else:
    #        dkimSecName = 'DEFAULT'
    #    dkimconfig[dkimSecName] = dict({str(k): str(v) for k, v in content.items()})
    dkimconfig = getConfigOf('dkim', cf)
    # apply general config defaults and the default section
    dkimconfig = applyDefault(dkimconfig, defaultDKIMConfig) # must be here because following section depends on default values

    #for dkimSecName, content in dkimconfig.items():
    #    if 'keysize' not in content:
    #        dkimconfig[dkimSecName]['keysize'] = 2048
    #    if 'keybasename' not in content:
    #        dkimconfig[dkimSecName]['keybasename'] = 'key'
    #    if 'keylocation' not in content:
    #        dkimconfig[dkimSecName]['keylocation'] = '/var/lib/rspamd/dkim'
    #    if 'signingconftemplatefile' not in content:
    #        dkimconfig[dkimSecName]['signingconftemplatefile'] = './dkim_signing_template.conf'
    #    if 'signingconftemporaryfile' not in content:
    #        dkimconfig[dkimSecName]['signingconftemporaryfile'] = '/etc/rspamd/dkim_signing_new.conf'
    #    if 'signingconfdestinationfile' not in content:
    #        dkimconfig[dkimSecName]['signingconftemplatefile'] = '/etc/rspamd/local.d/dkim_signing.conf'
    return dkimconfig

def interpreteCertConfig(cf):
    defaultCertConfig = {'source': '/etc/letsencrypt/live', 'certname': 'fullchain.pem', 'keysize': 4096, 'extraflags': ''}
    #certconfig = {}
    #for name, content in cf.items():
    #    section = name.split(':')
    #    if 'certificate' != section[0]:
    #        continue
    #    if 2 == len(section):
    #        certSecName = section[1]
    #    else:
    #        certSecName = 'DEFAULT'
    #    certconfig[certSecName] = dict({str(k): str(v) for k, v in content.items()})
    certconfig = getConfigOf('certificate', cf)
    # apply general config defaults and the default section
    certconfig = applyDefault(certconfig, defaultCertConfig) # must be here because following section depends on default values



    for certSecName, content in certconfig.items():
        #if 'source' not in content:
        #    certconfig[certSecName]['source'] = '/etc/letsencrypt/live'
        if 'generator' in content:
            print('generator in content')
            if 'certbot' == str(content['generator']): # certbot default certificate location - overrides source config
                print('certbot is generator')
                certconfig[certSecName]['source'] = '/etc/letsencrypt/live'
        #if 'certname' not in content:
        #    certconfig[certSecName]['certname'] = 'fullchain.pem'
        if 'keysize' in content:
            certconfig[certSecName]['keysize'] = int(certconfig[certSecName]['keysize'])
        #else:
        #    certconfig[certSecName]['keysize'] = 4096
        if 'extraflags' in content:
            certconfig[certSecName]['extraflags'] = content['extraflags'].replace(' ', '').split(',')
        #else:
        #    certconfig[certSecName]['extraflags'] = []
        if 'conflictingservices' in content:
            conflictingservices = re.sub(' ', '', content['conflictingservices']).split(',')
            if '' == conflictingservices[0]:
                conflictingservices = []
            certconfig[certSecName]['conflictingservices'] = conflictingservices
    print(certconfig)
    return certconfig


def applyDefault(config, defaultConfig = {}):
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

def getConfigOf(getSection, config, domainOldStyle = False):
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

