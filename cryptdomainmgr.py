#!/usr/bin/env python
# -*- encoding: UTF8 -*-

from dnsupdate import dnsuptools 

from subprocess import *
import os
from parse import parse
import configparser
import time
from jinja2 import Template
import re

def findCert(path, curName = None, nameList = [], filename = 'fullchain.pem', cert = None):
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


class ManagedDomain:
    def __init__(self):
        self.dnsup = dnsuptools.DNSUpTools()
        self.confPar = configparser.ConfigParser()
        self.certconfig = {'generator': 'certbot', 'email': 'stefan.helmert@t-online.de', 'destination': '/etc/ssl', 'extraflags': '', 'source': '/etc/letsencrypt/live', 'certname': 'fullchain.pem', 'keysize': 4096, 'webservers': 'apache2, nginx'}
        self.domainconfig = {'myexample.net': {'ip4': 'auto', 'ip6': 'auto', 'hasdkim': True, 'gencert': True, 'certlocation': '', 'tlsa': 'auto', 'mx': {'mail.myexample.net': 10}}}
        self.dkimconfig = {'generator': 'rspamd', 'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'signingconftemplatefile': './dkim_signing_template.conf', 'signingconftemporaryfile': '/etc/rspamd/dkim_signing_new.conf', 'signingconfdestinationfile': '/etc/rspamd/local.d/dkim_signing.conf'}
        self.webservers = ['apache2', 'nginx']

    def readConfig(self, confFile):
        if confFile is None:
            return
        self.confPar.read(os.path.expanduser(confFile))
        self.domainconfig = self.confPar._sections
        print(self.domainconfig)
        self.certconfig = {}
        self.dkimconfig = {}
        self.webservers = []
        if 'certificate' in self.domainconfig:
            self.certconfig = dict(self.confPar['certificate'])
            del self.domainconfig['certificate']
            if 'source' not in self.certconfig:
                self.certconfig['source'] = '/etc/letsencrypt/live'
            if 'certname' not in self.certconfig:
                self.certconfig['certname'] = 'fullchain.pem'
            if 'keysize' not in self.certconfig:
                self.certconfig['keysize'] = 4096
            if 'webservers' in self.certconfig:
                self.webservers = re.sub(' ', '', self.certconfig['webservers']).split(',')
                if '' == self.webservers[0]:
                    self.webservers = []
            
        self.dkimconfig = {}
        if 'dkim' in self.domainconfig:
            self.dkimconfig = dict(self.confPar['dkim'])
            if 'keysize' not in self.dkimconfig:
                self.dkimconfig['keysize'] = 2048
            if 'keybasename' not in self.dkimconfig:
                self.dkimconfig['keybasename'] = 'key'
            if 'keylocation' not in self.dkimconfig:
                self.dkimconfig['keylocation'] = '/var/lib/rspamd/dkim'
            del self.domainconfig['dkim']
        for name, content in self.domainconfig.items():
            if 'mx' in content.keys():
                mx = content['mx']
                mxList = re.sub(' ', '', mx).split(',')
                mxPrioList = [mxParse(e) for e in mxList]
                mxPrioDict = {e[0]: e[1] for e in mxPrioList}
                self.domainconfig[name]['mx'] = dict(mxPrioDict)



    def createCert(self):
        if 'generator' not in self.certconfig:
            return
        if 'certbot' == self.certconfig['generator']:
            extraFlags = re.sub(' ', '', self.certconfig['extraflags']).split(',')
            print([k for k, v in self.domainconfig.items() if parseBool(v['gencert'])])
            createCert([k for k, v in self.domainconfig.items() if 'gencert' in v and parseBool(v['gencert'])], self.certconfig['email'], self.certconfig['keysize'], extraFlags)

    def findCert(self, name, content):
        certlocation = None
        if 'certlocation' in content:
            certlocation = content['certlocation']
            if 'auto' == certlocation:
                certlocation = None
        print('certlocation = %s' % certlocation)
        print('self.findCert = %s' % findCert(self.certconfig['source'], name, self.domainconfig.keys(), self.certconfig['certname'], certlocation))
        return findCert(self.certconfig['source'], name, self.domainconfig.keys(), self.certconfig['certname'], certlocation)

    def setIPs(self): 
        for name, content in self.domainconfig.items():
            if 'ip4' in content:
                self.dnsup.setA(name, content['ip4']) 
            if 'ip6' in content:
                self.dnsup.setAAAA(name, content['ip6']) 

    def addMX(self, delete = False):
        for name, content in self.domainconfig.items():
            if 'mx' in content:
                mx = content['mx']
                if type(mx) is str:
                    mx = {mx: 10}
                for k, v in mx.items():
                    self.dnsup.addMX(name, k, v)
                if delete is True:
                    self.dnsup.delMX(name, '*', mx.keys())
            
    def setMX(self):
        self.addMX(True)



    def addTLSA(self):
        for name, content in self.domainconfig.items():
            if 'tlsa' in content:
                self.dnsup.addTLSAfromCert(name, self.findCert(name, content), content['tlsa'])

    def setTLSA(self):
        for name, content in self.domainconfig.items():
            if 'tlsa' in content:
                self.dnsup.setTLSAfromCert(name, self.findCert(name, content), content['tlsa'])

    def copyCert(self):
        for name, content in self.domainconfig.items():
            src = os.path.dirname(self.findCert(name, content))
            rv = check_output(('cp', '-rfLT', str(src), os.path.join(self.certconfig['destination'], name)))


    def stop80(self):
        for server in self.webservers:
            rv = check_output(('systemctl', 'stop', str(server)))

    def start80(self):
        for server in self.webservers:
            rv = check_output(('systemctl', 'start', str(server)))

    def addDKIM(self):
        keys = findDKIMkeyTXT(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'])
        keys = [f[1] for f in keys]
	print(keys)
        for name, content in self.domainconfig.items():
            if 'hasdkim' in content:
                if parseBool(content['hasdkim']) is True:
                    print((name, keys))
                    self.dnsup.addDKIMfromFile(name, keys)

    def setDKIM(self):
	print('setDKIM')
        keys = findDKIMkeyTXT(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'])
        keys = [f[1] for f in keys]
        print(keys)
        for name, content in self.domainconfig.items():
            if 'hasdkim' in content:
                if parseBool(content['hasdkim']) is True:
                    print((name, keys))
                    self.dnsup.setDKIMfromFile(name, keys)

    def dkimPrepare(self):
        if 'generator' in self.dkimconfig:
            if 'rspamd' == self.dkimconfig['generator']:
                createDKIM(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'], self.dkimconfig['keysize'], self.dkimconfig['signingconftemplatefile'], self.dkimconfig['signingconftemporaryfile'])
            self.addDKIM()

    def dkimRollover(self):
        if 'generator' in self.dkimconfig:
            if 'rspamd' == self.dkimconfig['generator']:
                rv = check_output(('mv', self.dkimconfig['signingconftemporaryfile'], self.dkimconfig['signingconfdestinationfile']))
                rv = check_output(('systemctl', 'reload', 'rspamd'))

    def dkimCleanup(self):
        if 'generator' in self.dkimconfig:
            if 'rspamd' == self.dkimconfig['generator']:
                self.setDKIM()
                keyFiles = findDKIMkey(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'])
                keyFiles.sort()
                if 2 > len(keyFiles):
                    return
                del keyFiles[-1]
                for keyFile in keyFiles:
                    rv = check_output(('rm', keyFile[1]))

    def certPrepare(self):
        self.stop80()
        self.createCert()
        self.start80()
        self.addTLSA()

    def certRollover(self):
        self.copyCert()

    def certCleanup(self):
        self.setTLSA()


    def prepare(self, confFile = None):
        self.readConfig(confFile)
        self.setIPs()
        self.addMX()
        self.certPrepare()
        self.dkimPrepare()

    def rollover(self, confFile = None):
        self.readConfig(confFile)
        self.certRollover()
        self.dkimRollover()

    def cleanup(self, confFile = None):
        self.readConfig(confFile)
        self.certCleanup()
        self.dkimCleanup()




def createDKIM(keylocation, keybasename, keysize, signingConfTemplateFile, signingConfDestFile):
    keylocation = os.path.expanduser(keylocation)
    newKeyname = str(keybasename) + '_{:10d}'.format(int(time.time()))
    keyTxt = check_output(('rspamadm', 'dkim_keygen', '-b', str(int(keysize)), '-s', str(newKeyname), '-k', os.path.join(keylocation, newKeyname+'.key')))
    f = open(os.path.join(keylocation, newKeyname+'.txt'), 'w')
    f.write(keyTxt)
    f.close()
    rv = check_output(('chmod', '0440', os.path.join(keylocation, newKeyname) + '.key'))
    rv = check_output(('chown', '_rspamd:_rspamd', os.path.join(keylocation, newKeyname) + '.key'))
    f = open(os.path.expanduser(signingConfTemplateFile), 'r')
    templateContent = f.read()
    f.close()
    template = Template(templateContent)
    confDestContent = template.render(keyname = newKeyname, keylocation = keylocation)
    f = open(os.path.expanduser(signingConfDestFile), 'w')
    f.write(confDestContent)
    f.close()


    

def findDKIMkeyTXT(keylocation, keybasename, fileending = 'txt'):
    return findDKIMkey(keylocation, keybasename, fileending)

def findDKIMkey(keylocation, keybasename, fileending = '{}'):
    keylocation = os.path.expanduser(keylocation)
    keyfiles = [(parse(str(keybasename)+'_{:d}.'+str(fileending), f), os.path.join(keylocation, f)) for f in os.listdir(keylocation) if os.path.isfile(os.path.join(keylocation, f))]
    print(keyfiles)
    keyfiles = [(e[0][0], e[1]) for e in keyfiles if e[0] is not None]
    print(keyfiles)
    return keyfiles


def createCert(domainList, email, keysize = 4096, extraFlags = []):
    print(domainList)
    if 0 == len(domainList):
        return
    args = ['./certbot/certbot-auto', 'certonly', '--email', str(email), '--agree-tos', '--non-interactive', '--standalone', '--expand', '--rsa-key-size', str(int(keysize))]
    print(extraFlags)
    args.extend(extraFlags)
    for d in domainList:
        args.extend(['-d', str(d)])
    print(args)
    rv = check_output(args)
    return rv


