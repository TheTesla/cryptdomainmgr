#!/usr/bin/env python
# -*- encoding: UTF8 -*-

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


class ConfigReader:
    def __init__(self):
        self.cp = configparser.ConfigParser()
        self.filenameList = []
        self.domainconfig = {}
        self.certconfig = {}
        self.dkimconfig = {}
        self.conflictingservices = {}

    def setFilenames(self, filenames):
        if type(filenames) is str:
            filenames = [filenames]
        self.filenameList = filenames

    def addFilenames(self, filenames):
        if type(filenames) is str:
            filenames = [filenames]
        self.filenameList.extend(filenames)

    def open(self):
        self.cp = configparser.ConfigParser()
        self.cp.read(self.filenameList)
        
    def interprete(self):
        self.domainconfig = applyDefault(interpreteDomainConfig(self.cp))
        self.certconfig = applyDefault(interpreteCertConfig(self.cp))
        self.dkimconfig = applyDefault(interpreteDKIMConfig(self.cp))
        self.conflictingservices = getConflictingServices(self.certconfig)



def interpreteDomainConfig(cf):
    domainconfig = {}
    for name, content in cf.items():
        section = name.split(':')
        if 'domain' != section[0]:
            if '.' not in section[0]: # fallback if not domain:example.de but example.de
                continue
        if 2 == len(section):
            domain = section[1]
        else:
            domain = 'DEFAULT'
            if '.' in section[0]:
                domain = section[0] # fallback if not domain:example.de but example.de
        domainconfig[domain] = dict(content)
        if 'mx' in content.keys():
            mx = content['mx']
            mxList = re.sub(' ', '', mx).split(',')
            mxPrioList = [mxParse(e) for e in mxList]
            mxPrioDict = {e[0]: e[1] for e in mxPrioList}
            domainconfig[domain]['mx'] = dict(mxPrioDict)
        if 'hasdkim' in content:
            domainconfig[domain]['hasdkim'] = cf.getboolean(name, 'hasdkim')
        else:
            domainconfig[domain]['hasdkim'] = False
        if 'gencert' in content:
            domainconfig[domain]['gencert'] = cf.getboolean(name, 'gencert')
        else:
            domainconfig[domain]['gencert'] = False
        if 'tlsa' in content:
            tlsa = cf.get(name, 'tlsa')
            if 'auto' == tlsa:
                tlsa = [[3,0,1], [3,0,2], [3,1,1], [3,1,2], [2,0,1], [2,0,2], [2,1,1], [2,1,2]]
            else:
                tlsa = [[int(f) for f in e] for e in re.sub(' ', '', tlsa).split(',')]
            domainconfig[domain]['tlsa'] = tlsa
    return domainconfig

def interpreteDKIMConfig(cf):
    dkimconfig = {}
    for name, content in cf.items():
        section = name.split(':')
        if 'dkim' != section[0]:
            continue
        if 2 == len(section):
            dkimSecName = section[1]
        else:
            dkimSecName = 'DEFAULT'
        dkimconfig[dkimSecName] = dict(content)
        if 'keysize' not in content:
            dkimconfig[dkimSecName]['keysize'] = 2048
        if 'keybasename' not in content:
            dkimconfig[dkimSecName]['keybasename'] = 'key'
        if 'keylocation' not in content:
            dkimconfig[dkimSecName]['keylocation'] = '/var/lib/rspamd/dkim'
        if 'signingconftemplatefile' not in content:
            dkimconfig[dkimSecName]['signingconftemplatefile'] = './dkim_signing_template.conf'
        if 'signingconftemporaryfile' not in content:
            dkimconfig[dkimSecName]['signingconftemporaryfile'] = '/etc/rspamd/dkim_signing_new.conf'
        if 'signingconfdestinationfile' not in content:
            dkimconfig[dkimSecName]['signingconftemplatefile'] = '/etc/rspamd/local.d/dkim_signing.conf'
    return dkimconfig

def interpreteCertConfig(cf):
    certconfig = {}
    for name, content in cf.items():
        section = name.split(':')
        if 'certificate' != section[0]:
            continue
        if 2 == len(section):
            certSecName = section[1]
        else:
            certSecName = 'DEFAULT'
        certconfig[certSecName] = dict(content)
        if 'source' not in content:
            certconfig[certSecName]['source'] = '/etc/letsencrypt/live'
        if 'generator' in content:
            if 'certbot' == content['generator']: # certbot default certificate location - overrides source config
                certconfig[certSecName]['source'] = '/etc/letsencrypt/live'
        if 'certname' not in content:
            certconfig[certSecName]['certname'] = 'fullchain.pem'
        if 'keysize' in content:
            certconfig[certSecName]['keysize'] = cf.getint(name, 'keysize')
        else:
            certconfig[certSecName]['keysize'] = 4096
        if 'extraflags' in content:
            certconfig[certSecName]['extraflags'] = re.sub(' ', '', content['extraflags']).split(',')
        else:
            certconfig[certSecName]['extraflags'] = []
        if 'conflictingservices' in content:
            conflictingservices = re.sub(' ', '', content['conflictingservices']).split(',')
            if '' == conflictingservices[0]:
                conflictingservices = []
            certconfig[certSecName]['conflictingservices'] = conflictingservices
    return certconfig


def applyDefault(config):
    default = {}
    if 'DEFAULT' in config:
        default = config['DEFAULT']
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig

def getConflictingServices(certConfig):
    return {f for e in certConfig.values()if 'conflictingservices' in e for f in e['conflictingservices']}



