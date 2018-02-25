#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


from subprocess import check_output
import os
from parse import parse
import configparser
import time
from jinja2 import Template
from cdmconfighandler import *

from simplelogger import simplelogger as log
from dnsuptools import dnsuptools 

def findCert(path, curName = None, nameList = [], filename = 'fullchain.pem', cert = None):
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
    




class ManagedDomain:
    def __init__(self):
        self.cr = ConfigReader()
        self.dnsup = dnsuptools.DNSUpTools()
        self.confPar = configparser.ConfigParser()
        self.certconfig = {} 
        self.domainconfig = {} 
        self.dkimconfig = {} 
        self.webservers = [] 

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
            log.debug('Create Certificate -- Section: {}'.format(certSecName))
            domains = [k for k,v in self.cr.domainconfig.items() if 'certificate' in v and certSecName == v['certificate']]
            log.debug(certConfig)
            extraFlags = certConfig['extraflags']
            createCert(domains, certConfig['email'], certConfig['keysize'], extraFlags)

    def findCert(self, name, content):
	log.debug(self.cr.certconfig)
        try:
            certlocation = self.cr.certconfig[content['certificate']]['source']
        except:
            certlocation = None
        if 'certificate' in content:
            certSecName = content['certificate']
        else:
            certSecName = 'DEFAULT'
        domainsOfSameCert = [k for k,v in self.cr.domainconfig.items() if 'certificate' in v and certSecName == v['certificate']]
        log.debug('  domainsOfSameCert = ' + str(domainsOfSameCert))
        log.debug('  certlocation = %s' % certlocation)
        log.debug('  name = ' +str(name))
        if certSecName in self.cr.certconfig:
            certName = self.cr.certconfig[certSecName]['certname']
        else:
            certName = 'fullchain.pem'
        log.debug('  certname = ' +str(certName))
        cert = findCert(certlocation, name, domainsOfSameCert, certName, certlocation)
        log.debug('  self.findCert = %s' % cert)
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

    def addSRV(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'srvAggrAdd' in content:
                self.dnsup.addSRV(name, content['srvAggrAdd']) 

    def delSRV(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'srvAggrDel' in content:
                self.dnsup.delSRV(name, content['srvAggrDel'], content['srvAggrAdd']) 

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

    def addMX(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'mxAggrAdd' in content:
                for mx in content['mxAggrAdd']:
                    self.dnsup.addMX(name, mx['content'], mx['prio']) 
            
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

    def delMX(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'mxAggrDel' in content:
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
                cert = self.findCert(name, content)
                if cert is None:
                    log.info('{} has no cert'.format(name))
                else:
                    self.dnsup.addTLSAfromCert(name, cert, content['tlsa'])

    def setTLSA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'tlsa' in content:
                cert = self.findCert(name, content)
                if cert is None:
                    log.info('{} has no cert'.format(name))
                else:
                    self.dnsup.setTLSAfromCert(name, cert, content['tlsa'])

    def copyCert(self):
        for name, content in self.cr.domainconfig.items():
            log.debug(name)
            if 'DEFAULT' == name:
                continue
            if 'certificate' not in content:
                continue
            src = os.path.dirname(self.findCert(name, content))
            dest = os.path.join(self.cr.certconfig[content['certificate']]['destination'], name)
            log.debug('Copy Certificate')
            log.debug('  {} -> {}'.format(src, dest))
            rv = check_output(('cp', '-rfLT', str(src), str(dest)))


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
            log.debug(keys)
            for name, content in domainsOfSameDKIM.items():
                log.debug((name, keys))
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
            log.info("Preparing DKIM key for dkim-section: \"{}\"".format(dkimSecName))
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
                keyFiles = findDKIMkey(dkimContent['keylocation'], dkimContent['keybasename'])
                keyFiles.sort()
                if 2 > len(keyFiles):
                    return
                del keyFiles[-1]
                for keyFile in keyFiles:
                    rv = check_output(('rm', keyFile[1]))
                # set records after deleting, to delete all records, where the files are already deleted 
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

    def update(self, state = '', confFile = None):
        self.readConfig(confFile)
        self.setCAA()
        self.addCAA()
        self.setSOA()
        self.setSPF()
        self.addSPF()
        self.setADSP()
        self.setDMARC()
        self.setSRV()
        self.addSRV()
        self.delSRV()
        self.setIPs()
        self.addIPs()
        # self.setMX() # preplaced by addMX() and delMX()
        self.addMX()
        self.delMX()
        if 'prepare' == state:
            self.addDKIM()
            self.addTLSA()
        elif 'cleanup' == state:
            self.setDKIM()
            self.setTLSA()

    def prepare(self, confFile = None):
        self.readConfig(confFile)
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
    log.debug(keyfiles)
    keyfiles = [(e[0][0], e[1]) for e in keyfiles if e[0] is not None]
    log.debug(keyfiles)
    return keyfiles


def createCert(domainList, email, keysize = 4096, extraFlags = []):
    log.debug(domainList)
    if 0 == len(domainList):
        return
    args = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certbot/certbot-auto'), 'certonly', '--email', str(email), '--agree-tos', '--non-interactive', '--standalone', '--expand', '--rsa-key-size', str(int(keysize))]
    log.debug(extraFlags)
    args.extend(extraFlags)
    for d in domainList:
        args.extend(['-d', str(d)])
    log.debug(args)
    rv = check_output(args)
    return rv


