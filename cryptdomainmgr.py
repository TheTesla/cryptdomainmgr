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
from cdmconfighandler import *


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
        self.cr = ConfigReader()
        self.dnsup = dnsuptools.DNSUpTools()
        self.confPar = configparser.ConfigParser()
        self.certconfig = {} #{'generator': 'certbot', 'email': 'stefan.helmert@t-online.de', 'destination': '/etc/ssl', 'extraflags': '', 'source': '/etc/letsencrypt/live', 'certname': 'fullchain.pem', 'keysize': 4096, 'webservers': 'apache2, nginx'}
        self.domainconfig = {} #{'myexample.net': {'ip4': 'auto', 'ip6': 'auto', 'hasdkim': True, 'gencert': True, 'certlocation': '', 'tlsa': 'auto', 'mx': {'mail.myexample.net': 10}}}
        self.dkimconfig = {} #{'generator': 'rspamd', 'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'signingconftemplatefile': './dkim_signing_template.conf', 'signingconftemporaryfile': '/etc/rspamd/dkim_signing_new.conf', 'signingconfdestinationfile': '/etc/rspamd/local.d/dkim_signing.conf'}
        self.webservers = [] #['apache2', 'nginx']

    def readConfig(self, confFiles):
        self.cr.setFilenames(confFiles)
        self.cr.open()
        self.cr.interprete()
        self.dnsupLoginConf()



    def dnsupLoginConf(self):
        userDict = {k: v['user'] for k, v in self.cr.domainconfig.items() if 'user' in v}
        self.dnsup.setUserDict(userDict)
        if 'DEFAULT' in userDict.keys():
            userDict['default'] = userDict['DEFAULT'] 
        passwdDict = {k: v['passwd'] for k, v in self.cr.domainconfig.items() if 'passwd' in v}
        if 'DEFAULT' in passwdDict.keys():
            passwdDict['default'] = passwdDict['DEFAULT'] 
        self.dnsup.setPasswdDict(passwdDict)


    def createCert(self):
        for certSecName, certConfig in self.cr.certconfig.items():
            if 'generator' not in certConfig:
                continue
            if 'certbot' != certConfig['generator']:
                continue
            domains = [k for k,v in self.cr.domainconfig.items() if 'certificate' in v and certSecName == v['certificate']]
            print('createCert')
            print(certConfig)
            extraFlags = certConfig['extraflags']
            createCert(domains, certConfig['email'], certConfig['keysize'], extraFlags)

    def findCert(self, name, content):
        try:
            certlocation = self.cr.certconfig[content['certificate']]['source']
        except:
            certlocation = None
        if 'certificate' in content:
            certSecName = content['certificate']
        else:
            certSecName = 'DEFAULT'
        domainsOfSameCert = [k for k,v in self.cr.domainconfig.items() if 'certificate' in v and certSecName == v['certificate']]
	print('domainsOfSameCert = ' + str(domainsOfSameCert))
        print('certlocation = %s' % certlocation)
	print('name = ' +str(name))
	print('certname = ' +str(self.cr.certconfig[content['certificate']]['certname']))
        cert = findCert(certlocation, name, domainsOfSameCert, self.cr.certconfig[content['certificate']]['certname'], certlocation)
        print('self.findCert = %s' % cert)
        return cert


    def addSPF(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'spf+' in content:
                self.dnsup.setSPFentry(name, content['spf+'])

    def setSPF(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'spf' in content:
                self.dnsup.setSPF(name, content['spf'])

    def setDMARC(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'dmarc' in content:
                self.dnsup.setDMARCentry(name, content['dmarc'])

    def setADSP(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'adsp' in content:
                self.dnsup.setADSP(name, content['adsp'])

    def setSOA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'soa' in content:
                self.dnsup.setSOAentry(name, content['soa'])
    
    def setSRV(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'srv' in content:
                self.dnsup.setSRV(name, content['srv'])

    def addCAA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'caa+' in content:
                self.dnsup.addCAA(name, content['caa+'])

    def setCAA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'caa' in content:
                self.dnsup.setCAA(name, content['caa'])

    def setIPs(self): 
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'ip4' in content:
                self.dnsup.setA(name, content['ip4']) 
            if 'ip6' in content:
                self.dnsup.setAAAA(name, content['ip6']) 

    def addIPs(self): 
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'ip4+' in content:
                self.dnsup.addA(name, content['ip4+']) 
            if 'ip6+' in content:
                self.dnsup.addAAAA(name, content['ip6+']) 

    def addMX(self, delete = False):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            #if 'mxAdd' in content:
            #    for mx in content['mxAdd']:
            #        self.dnsup.addMX(name, mx['content'], mx['addprio']) 
            if 'mxAggrAdd' in content:
                for mx in content['mxAggrAdd']:
                    self.dnsup.addMX(name, mx['content'], mx['prio']) 

            #if 'mx' in content:
            #    mx = content['mx']
            #    if type(mx) is str:
            #        mx = {mx: 10}
            #    for k, v in mx.items():
            #        self.dnsup.addMX(name, k, v)
            #    if delete is True:
            #        self.dnsup.delMX(name, '*', mx.keys())
            
    def setMX(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'mxSet' in content:
                for mx in content['mxSet']:
                    self.dnsup.addMX(name, mx['content'], mx['addprio']) 
                delList = [{'prio': e['delprio']} for e in content['mxSet']]
                if '*' in [e['prio'] for e in delList]:
                    delList = [{}]
                presList = [{'prio': e['addprio'], 'content': e['content']} for e in content['mxSet']]
                self.dnsup.delDictList({'name': name, 'type': 'MX'}, delList, presList)
        #self.addMX(True)

    def delMX(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'mxAggrDel' in content:
                #delList = [{'prio': e['prio']} for e in content['mxAggrDel']]
                delList = content['mxAggrDel']
                for e in delList:
                    del e['key']
                presList = content['mxAggrAdd']
                for e in presList:
                    del e['key']
                self.dnsup.delDictList({'name': name, 'type': 'MX'}, delList, presList)



    def addTLSA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'tlsa' in content:
                self.dnsup.addTLSAfromCert(name, self.findCert(name, content), content['tlsa'])

    def setTLSA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'tlsa' in content:
                self.dnsup.setTLSAfromCert(name, self.findCert(name, content), content['tlsa'])

    def copyCert(self):
        for name, content in self.cr.domainconfig.items():
            print(name)
            if 'DEFAULT' == name:
                continue
            if 'certificate' not in content:
                continue
            src = os.path.dirname(self.findCert(name, content))
            print(src)
            rv = check_output(('cp', '-rfLT', str(src), os.path.join(self.cr.certconfig[content['certificate']]['destination'], name)))


    def stop80(self):
        for server in self.cr.conflictingservices:
            rv = check_output(('systemctl', 'stop', str(server)))

    def start80(self):
        for server in self.cr.conflictingservices:
            rv = check_output(('systemctl', 'start', str(server)))

    def addDKIM(self, delete = False):
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            keys = findDKIMkeyTXT(dkimContent['keylocation'], dkimContent['keybasename'])
            keys = [f[1] for f in keys]
            domainsOfSameDKIM = {k:v for k, v in self.cr.domainconfig.items() if 'dkim' in v and dkimSecName == v['dkim']}
            print(keys)
            for name, content in domainsOfSameDKIM.items():
                print((name, keys))
                if delete is True:
                    self.dnsup.setDKIMfromFile(name, keys)
                else:
                    self.dnsup.addDKIMfromFile(name, keys)

    def setDKIM(self):
        self.addDKIM(True)

    def dkimPrepare(self):
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            if 'generator' not in dkimContent:
                continue
            if 'rspamd' == dkimContent['generator']:
                createDKIM(dkimContent['keylocation'], dkimContent['keybasename'], dkimContent['keysize'], dkimContent['signingconftemplatefile'], dkimContent['signingconftemporaryfile'])
            self.addDKIM()

    def dkimRollover(self):
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            if 'generator' not in dkimContent:
                continue
            if 'rspamd' == dkimContent['generator']:
                rv = check_output(('mv', dkimContent['signingconftemporaryfile'], dkimContent['signingconfdestinationfile']))
                rv = check_output(('systemctl', 'reload', 'rspamd'))

    def dkimCleanup(self):
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            if 'generator' not in dkimContent:
                continue
            if 'rspamd' == dkimContent['generator']:
                self.setDKIM()
                keyFiles = findDKIMkey(dkimContent['keylocation'], dkimContent['keybasename'])
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
        self.setCAA()
        self.addCAA()
        self.setSOA()
        self.setSPF()
        self.addSPF()
        self.setADSP()
        self.setDMARC()
        self.setSRV()
        self.setIPs()
        self.addIPs()
        #self.setMX()
        self.addMX()
        self.delMX()
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


