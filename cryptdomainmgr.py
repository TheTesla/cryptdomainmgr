#!/usr/bin/env python
# -*- encoding: UTF8 -*-

from dnsupdate import dnsuptools 

from subprocess import *
import os
from parse import parse
import configparser
import time
from jinja2 import Template

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
    


class ManagedDomain:
    def __init__(self):
        self.dnsup = dnsuptools.DNSUpTools()
        self.confPar = configparser.ConfigParser()
        self.certconfig = {'generator': 'certbot', 'email': 'stefan.helmert@t-online.de', 'destination': '/etc/ssl', 'extraflags': '', 'source': '/etc/letsencrypt/live', 'certname': 'fullchain.pem', 'keysize': 4096}
        self.domainconfig = {'myexample.net': {'ip4': 'auto', 'ip6': 'auto', 'hasdkim': True, 'gencert': True, 'certlocation': '', 'tlsa': 'auto', 'mx': {'mail.myexample.net': 10}}}
        self.dkimconfig = {'generator': 'rspamd', 'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'signingConfTemplateFile': './dkim_signing_template.conf', 'signingConfTemporaryFile': '/etc/rspamd/dkim_signing_new.conf', 'signingConfDestinationFile': '/etc/rspamd/local.d/dkim_signing.conf'}
        self.webservers = ['apache2', 'nginx']

    def readConfig(self, confFile):
        if confFile is None:
            return
        self.confPar.read(os.path.expanduser(confFile))
        self.domainconfig = dict(self.confPar)
        self.certconfig = {}
        if 'certificate' in self.domainconfig:
            self.certconfig = dict(self.confPar['certificate'])
            del self.domainconfig['certificate']
        self.dkimconfig = {}
        if 'dkimconfig' in self.domainconfig:
            self.dkimconfig = dict(self.confPar['dkimconfig'])
            del self.domainconfig['dkimconfig']

    def createCert(self):
        if 'certbot' == self.certconfig['generator']:
            createCert([k for k, v in self.domainconfig.items() if 'gencert' in v and True == v['gencert']], self.certconfig['email'], self.certconfig['keysize'], self.certconfig['extraflags'])

    def findCert(self, name, content):
        if 'certlocation' in content:
            certlocation = content['certlocation']
        else:
            certlocation = None
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
                self.dnsup.addTLSAfromCert(self.findCert(name, content), content['tlsa'])

    def setTLSA(self):
        for name, content in self.domainconfig.items():
            if 'tlsa' in content:
                self.dnsup.setTLSAfromCert(self.findCert(name, content), content['tlsa'])

    def copyCert(self):
        for name, content in self.domainconfig.items():
            src = os.path.basename(self.findCert(name, content))
            rv = check_output(('cp', '-rfL', str(src), os.path.join(self.domainconfig['destination'], name)))


    def stop80(self):
        for server in self.webservers:
            rv = check_output(('systemctl', 'stop', str(server)))

    def start80(self):
        for server in self.webservers:
            rv = check_output(('systemctl', 'start', str(server)))

    def addDKIM(self):
        keys = findDKIMkeyTXT(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'])
        for name, content in self.domainconfig.items():
            if content['hasdkim'] is True:
                self.dnsup.addDKIMfromFile(name, keys)

    def setDKIM(self):
        keys = findDKIMkeyTXT(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'])
        for name, content in self.domainconfig.items():
            if content['hasdkim'] is True:
                self.dnsup.setDKIMfromFile(name, keys)

    def dkimPrepare(self):
        if 'generator' in self.dkimconfig:
            if 'rspamd' == self.dkimconfig['generator']
                createDKIM(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'], self.dkimconfig['keysize'], self.dkimconfig['signingConfTemplateFile'], self.dkimconfig['signingConfTemporaryFile'])
        self.addDKIM()

    def dkimRollover(self):
        if 'generator' in self.dkimconfig:
            if 'rspamd' == self.dkimconfig['generator']
                rv = check_output(('mv', self.dkimconfig['signingConfTemporaryFile'], self.dkimconfig['signingConfDestinationFile']))
                rv = check_output(('systemctl', 'relaod', 'rspamd'))

    def dkimCleanup(self):
        keyFiles = findDKIMkey(self.dkimconfig['keylocation'], self.dkimconfig['keybasename'])
        keyFiles.sort()
        if 2 > len(keyFiles):
            return
        del keyFiles[-1]
        for keyFile in keyfiles:
            rv = check_output(('rm', keyFile[1]))
        self.setDKIM()

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
    newKeyname = str(keybasename) + '_{:10d}'.format(int(time.time())
    keyTxt = check_output(('rspamd', 'dkim_keygen', '-b', str(int(keysize)), '-s', str(newKeyname), '-k', os.path.join(keylocation, newKeyname+'.key'))
    f = open(os.path.join(keylocation, newKeyname+'.txt'), 'w')
    f.write(f)
    f.close()
    rv = check_output(('chmod', '0440', os.path.join(keylocation, newKeyname) + '.*'))
    rv = check_output(('chown', '_rspamd:_rspamd', os.path.join(keylocation, newKeyname) + '.*'))
    f = open(os.path.expanduser(signingConfTemplateFile), 'r')
    templateContent = f.read()
    f.close()
    template = Template(templateContent)
    confDestContent = template.reander(keyname = newKeyname)
    f = open(os.path.expanduser(signingConfDestFile), 'w')
    f.write(confDestContent)
    f.close()


    

def findDKIMkeyTXT(keylocation, keybasename, fileending = 'txt'):
    findDKIMkey(keylocation, keybasename, fileending)

def findDKIMkey(keylocation, keybasename, fileending = '{}'):
    keylocation = os.path.expanduser(keylocation)
    keyfiles = [(parse(str(keybasename)+'_{:d}.'+str(fileending), f), os.path.join(keylocation, f)) for f in os.listdir(keylocation) if os.isfile(os.path.join(keylocation, f))]
    keyfiles = [e for e in keyfiles if e[0] is not None]
    return keyfiles


def createCert(domainList, email, keysize = 4096, extraFlags = []):
    args = ['./certbot/certbot-auto', 'certonly', '--email', str(email), '--agree-tos', '--non-interactive', '--standalone', '--expand', '--rsa-key-size', str(int(keysize))]
    for e in extraFlags:
        args.extend(e)
    for d in domainList:
        args.extend(['-d', str(d)])
    print(args)
    rv = check_output(args)
    return rv


