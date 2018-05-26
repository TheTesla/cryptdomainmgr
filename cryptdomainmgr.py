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
from OpenSSL import crypto

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
        self.dnsup.setHandler('inwx')
        self.dnsup.handler.setUserDict(userDict)
        if 'DEFAULT' in userDict.keys():
            userDict['default'] = userDict['DEFAULT'] 
        passwdDict = {k: v['passwd'] for k, v in self.cr.domainconfig.items() if 'passwd' in v}
        if 'DEFAULT' in passwdDict.keys():
            passwdDict['default'] = passwdDict['DEFAULT'] 
        self.dnsup.handler.setPasswdDict(passwdDict)


    def createCert(self):
        for certSecName, certConfig in self.cr.certconfig.items():
            if 'generator' not in certConfig:
                continue
            if 'certbot' != certConfig['generator']:
                continue
            log.info('Create certificate for section \"{}\"'.format(certSecName))
            domains = [k for k,v in self.cr.domainconfig.items() if 'certificate' in v and certSecName == v['certificate']]
            extraFlags = certConfig['extraflags']
            log.info('  -> {}'.format(', '.join(domains)))
            log.debug(certConfig)
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

    def setSPF(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'spfAggrDel' in content and 'spfAggrAdd' in content:
                self.dnsup.setSPFentry(name, content['spfAggrAdd'], content['spfAggrDel'])
            elif 'spfAggrDel' in content:
                self.dnsup.setSPFentry(name, {}, content['spfAggrDel'])
            elif 'spfAggrAdd' in content:
                self.dnsup.setSPFentry(name, content['spfAggrAdd'], {})

    def setDMARCentries(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'dmarc' in content:
                # following line means configuration:
                # dmarc = 
                # this deletes all entries not specified
                # if no configuration like:
                # dmarc = 
                # is specified, so only given dmarc subparameters are overwritten
                # all this is managed by dnsuptools:
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

    def setSRV(self):
        self.addSRV()
        self.delSRV()

    def addCAA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'caaAggrAdd' in content:
                self.dnsup.addCAA(name, content['caaAggrAdd'])

    def delCAA(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'caaAggrDel' in content:
                self.dnsup.delCAA(name, content['caaAggrDel'], content['caaAggrAdd'])

    def setCAA(self):
        self.addCAA()
        self.delCAA()

    def delIPs(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'ip4AggrDel' in content:
                self.dnsup.delA(name, [e['content'] if 'content' in e else '*' for e in content['ip4AggrDel']], [e['content']  for e in content['ip4AggrAdd']]) 
            if 'ip6AggrDel' in content:
                self.dnsup.delAAAA(name, [e['content'] if 'content' in e else '*' for e in content['ip6AggrDel']], [e['content']  for e in content['ip6AggrAdd']]) 

    def addIPs(self): 
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'ip4AggrAdd' in content:
                self.dnsup.addA(name, [e['content']  for e in content['ip4AggrAdd']]) 
            if 'ip6AggrAdd' in content:
                self.dnsup.addAAAA(name, [e['content']  for e in content['ip6AggrAdd']]) 

    def setIPs(self): 
        self.addIPs()
        self.delIPs()

    def addMX(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'mxAggrAdd' in content:
                self.dnsup.addMX(name, content['mxAggrAdd'])
            
    def delMX(self):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'mxAggrDel' in content:
                self.dnsup.delMX(name, content['mxAggrDel'], content['mxAggrAdd'])

    def setMX(self):
        self.addMX()
        self.delMX()

    def addTLSA(self):
        self.setTLSA(True)

    def setTLSA(self, addOnly = False):
        for name, content in self.cr.domainconfig.items():
            if 'DEFAULT' == name:
                continue
            if 'tlsa' in content:
                cert = self.findCert(name, content)
                if cert is None:
                    log.info('not deploying TLSA record for {} (no certificate)'.format(name))
                else:
                    log.info('deploying TLSA record for {} (certificate found)'.format(name))
                    sanList = getCertSAN(cert)
                    log.info('  -> found certificate: {} for: {}'.format(cert, ', '.join(sanList)))
                    if name not in sanList:
                        log.error('{} not in certificate {}'.format(name, cert))
                    if addOnly is True:
                        self.dnsup.addTLSAfromCert(name, cert, content['tlsa'])
                    else:
                        self.dnsup.setTLSAfromCert(name, cert, content['tlsa'])

    def copyCert(self):
        log.info('Copy certificate')
        for name, content in self.cr.domainconfig.items():
            log.debug(name)
            if 'DEFAULT' == name:
                continue
            if 'certificate' not in content:
                continue
            src = os.path.dirname(self.findCert(name, content))
            dest = os.path.join(self.cr.certconfig[content['certificate']]['destination'], name)
            log.info('  {} -> {}'.format(src, dest))
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
        log.info('DKIM prepare')
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
        log.info('DKIM rollover')
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            if 'generator' not in dkimContent:
                continue
            if 'rspamd' == dkimContent['generator']:
                log.info('using new dkim key, moving new config file')
                log.info('  {} -> {}'.format(dkimContent['signingconftemporaryfile'], dkimContent['signingconfdestinationfile']))
                rv = check_output(('mv', dkimContent['signingconftemporaryfile'], dkimContent['signingconfdestinationfile']))
                log.info('reloading rspamd')
                rv = check_output(('systemctl', 'reload', 'rspamd'))

    def dkimCleanup(self):
        log.info('DKIM cleanup')
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
                del keyFiles[-2:]
                for keyFile in keyFiles:
                    log.info('  rm {}'.format(keyFile[1]))
                    rv = check_output(('rm', keyFile[1]))
                self.setDKIM()

    def certPrepare(self):
        log.info('Certificate prepare')
        self.stop80()
        self.createCert()
        self.start80()
        self.addTLSA()

    def certRollover(self):
        log.info('Certificate rollover')
        self.copyCert()

    def certCleanup(self):
        log.info('Certificate cleanup')
        self.setTLSA()

    def update(self, state = '', confFile = None):
        self.readConfig(confFile)
        self.setCAA()
        self.setSOA()
        self.setSPF() # add and del entries
        self.setADSP()
        self.setDMARCentries()
        self.setSRV() # contains addSRV() and delSRV() 
        self.setIPs()
        self.setMX() # contains addMX() and delMX()
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


def getCertSAN(filename):
    certFile = open(filename, 'rt').read()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certFile)
    san = [cert.get_extension(i).get_data().split('\x82')[1:] for i in range(cert.get_extension_count()) if 'subjectAltName' == cert.get_extension(i).get_short_name()][0]
    san = [e[1:] for e in san]
    return san





