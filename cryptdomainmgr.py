#!/usr/bin/env python
# -*- encoding: UTF8 -*-

from dnsupdate import dnsuptools 

from subprocess import *
import os.path
import configparser

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
        self.domainconfig = {'myexamle.net': {'ip4': 'auto', 'ip6': 'auto', 'gencert': True, 'certlocation': '', 'tlsa': 'auto'}}


    def readConfig(self, confFile):
        if confFile is None:
            return
        self.confPar.read(os.path.expanduser(confFile))
        self.certconfig = dict(self.confPar['certificate'])
        self.domainconfig = dict(self.confPar)
        if 'certificate' in self.domainconfig:
            del self.domainconfig['certificate']


    def createCert(self):
        if 'certbot' == self.certconfig['generator']:
            createCert([k for k, v in self.domainconfig.items() if 'gencert' in v and True == v['gencert']], self.certconfig['email'], self.certconfig['keysize'], self.certconfig['extraflags'])

    def setIPs(self): 
        for name, content in self.domainconfig.items():
            if 'ip4' in content:
                self.dnsup.setA(name, content['ip4']) 
            if 'ip6' in content:
                self.dnsup.setAAAA(name, content['ip6']) 

    def addTLSA(self):
        for name, content in self.domainconfig.items():
            if 'tlsa' in content:
                if 'certlocation' in content:
                    certlocation = content['certlocation']
                else:
                    certlocation = None
                self.dnsup.addTLSAfromCert(findCert(self.certconfig['source'], name, self.domainconfig.keys(), self.certconfig['certname'], certlocation), content['tlsa'])

    def setTLSA(self):
        for name, content in self.domainconfig.items():
            if 'tlsa' in content:
                if 'certlocation' in content:
                    certlocation = content['certlocation']
                else:
                    certlocation = None
                self.dnsup.setTLSAfromCert(findCert(self.certconfig['source'], name, self.domainconfig.keys(), self.certconfig['certname'], certlocation), content['tlsa'])


    def copyCert(self):
        for name, content in self.domainconfig.items():
            if 'certlocation' in content:
                certlocation = content['certlocation']
            else:
                certlocation = None
            src = os.path.basename(findCert(self.certconfig['source'], name, self.domainconfig.keys(), self.certconfig['certname'], certlocation))
            rv = check_output(('cp', '-rfL', str(src), os.path.join(self.domainconfig['destination'], name)))


    def prepare(self, confFile = None):
        self.readConfig(confFile)
        self.setIPs()
        self.createCert()
        self.addTLSA()

    def rollover(self, confFile = None):
        self.readConfig(confFile)
        self.copyCert()

    def cleanup(self, confFile = None):
        self.readConfig(confFile)
        self.setTLSA()
        



def createCert(domainList, email, keysize = 4096, extraFlags = []):
    args = ['./certbot/certbot-auto', 'certonly', '--email', str(email), '--agree-tos', '--non-interactive', '--standalone', '--expand', '--rsa-key-size', str(int(keysize))]
    for e in extraFlags:
        args.extend(e)
    for d in domainList:
        args.extend(['-d', str(d)])
    print(args)
    rv = check_output(args)
    return rv


