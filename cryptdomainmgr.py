#!/usr/bin/env python
# -*- encoding: UTF8 -*-

from dnsupdate import dnsuptools 

from subprocess import *
import os.path


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
        self.certconfig = {'email': 'stefan.helmert@t-online.de', 'destination': '/etc/ssl', 'extraflags': '', 'source': '/etc/letsencrypt/live', 'certname': 'fullchain.pem', 'keysize': 4096}
        self.domainconfig = {'myexamle.net': {'ip4': 'auto', 'ip6': 'auto', 'cert': 'auto', 'tlsa': 'auto'}}
        
    def createCert(self):
        createCert([k for k, v in self.domainconfig.items() if 'auto' == v['cert']], self.certconfig['email'], self.certconfig['keysize'], self.certconfig['extraflags'])

    def setIPs(self): 
        for name, content in self.domainconfig.items():
            if 'ip4' in content:
                self.dnsup.setA(name, content['ip4']) 
            if 'ip6' in content:
                self.dnsup.setAAAA(name, content['ip6']) 

    def addTLSA(self):
        for name, content in self.domainconfig.items():
            if 'cert' in content:
                self.dnsup.addTLSAfromCert(findCert(self.certconfig['source'], name, self.domainconfig.keys(), self.certconfig['certname'], content['cert']), content['tlsa'])


    def prepare(self):
        self.setIPs()
        self.createCert()
        self.addTLSA()



def createCert(domainList, email, keysize = 4096, extraFlags = []):
    args = ['./certbot/certbot-auto', 'certonly', '--email', str(email), '--agree-tos', '--non-interactive', '--standalone', '--expand', '--rsa-key-size', str(int(keysize))]
    for e in extraFlags:
        args.extend(e)
    for d in domainList:
        args.extend(['-d', str(d)])
    print(args)
    rv = check_output(args)
    return rv


