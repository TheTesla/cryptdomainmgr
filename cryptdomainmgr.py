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
from modules.certificate import certbot as certmodule
from modules.certificate.main import getCertSAN, findCert, createCert, copyCert

from simpleloggerplus import simpleloggerplus as log
from dnsuptools import dnsuptools 
from OpenSSL import crypto

class ManagedDomain:
    def __init__(self):
        self.cr = ConfigReader()
        self.dnsup = dnsuptools.DNSUpTools()
        self.confPar = configparser.ConfigParser()

    def readConfig(self, confFiles):
        self.cr.setFilenames(confFiles)
        self.cr.open()
        self.cr.interprete()
        self.dnsupLoginConf()



    def dnsupLoginConf(self):
        userDict = {k: v['user'] for k, v in self.cr.config['domain'].items() if 'user' in v}
        self.dnsup.setHandler('inwx')
        self.dnsup.handler.setUserDict(userDict)
        if 'DEFAULT' in userDict.keys():
            userDict['default'] = userDict['DEFAULT'] 
        passwdDict = {k: v['passwd'] for k, v in self.cr.config['domain'].items() if 'passwd' in v}
        if 'DEFAULT' in passwdDict.keys():
            passwdDict['default'] = passwdDict['DEFAULT'] 
        self.dnsup.handler.setPasswdDict(passwdDict)


    def setSPF(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'spfAggrDel' in content and 'spfAggrAdd' in content:
                self.dnsup.setSPFentry(name, content['spfAggrAdd'], content['spfAggrDel'])
            elif 'spfAggrDel' in content:
                self.dnsup.setSPFentry(name, {}, content['spfAggrDel'])
            elif 'spfAggrAdd' in content:
                self.dnsup.setSPFentry(name, content['spfAggrAdd'], {})

    def setDMARCentries(self):
        for name, content in self.cr.config['domain'].items():
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
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'adsp' in content:
                self.dnsup.setADSP(name, content['adsp'])

    def setSOA(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'soa' in content:
                self.dnsup.setSOAentry(name, content['soa'])
    
    def addSRV(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'srvAggrAdd' in content:
                self.dnsup.addSRV(name, content['srvAggrAdd']) 

    def delSRV(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'srvAggrDel' in content:
                self.dnsup.delSRV(name, content['srvAggrDel'], content['srvAggrAdd']) 

    def setSRV(self):
        self.addSRV()
        self.delSRV()

    def addCAA(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'caaAggrAdd' in content:
                self.dnsup.addCAA(name, content['caaAggrAdd'])

    def delCAA(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'caaAggrDel' in content:
                self.dnsup.delCAA(name, content['caaAggrDel'], content['caaAggrAdd'])

    def setCAA(self):
        self.addCAA()
        self.delCAA()

    def delIPs(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'ip4AggrDel' in content:
                self.dnsup.delA(name, [e['content'] if 'content' in e else '*' for e in content['ip4AggrDel']], [e['content']  for e in content['ip4AggrAdd']]) 
            if 'ip6AggrDel' in content:
                self.dnsup.delAAAA(name, [e['content'] if 'content' in e else '*' for e in content['ip6AggrDel']], [e['content']  for e in content['ip6AggrAdd']]) 

    def addIPs(self): 
        for name, content in self.cr.config['domain'].items():
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
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'mxAggrAdd' in content:
                self.dnsup.addMX(name, content['mxAggrAdd'])
            
    def delMX(self):
        for name, content in self.cr.config['domain'].items():
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
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'tlsa' in content:
                cert = findCert(name, content, self.cr.config)
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
            domainsOfSameDKIM = {k:v for k, v in self.cr.config['domain'].items() if 'dkim' in v and dkimSecName == v['dkim']}
            log.debug(keys)
            for name, content in domainsOfSameDKIM.items():
                log.debug((name, keys))
                if delete is True:
                    self.dnsup.setDKIMfromFile(name, keys)
                else:
                    self.dnsup.addDKIMfromFile(name, keys)

    def setDKIM(self):
        self.addDKIM(True)

    def dkimPrepare(self, i=2):
        if i != 2:
            return
        log.info('DKIM prepare')
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            log.info("Preparing DKIM key for dkim-section: \"{}\"".format(dkimSecName))
            if 'handler' not in dkimContent:
                continue
            if 'rspamd' == dkimContent['handler']:
                createDKIM(dkimContent['keylocation'], dkimContent['keybasename'], dkimContent['keysize'], dkimContent['signingconftemplatefile'], dkimContent['signingconftemporaryfile'])
            self.addDKIM()

    def dkimRollover(self, i=2):
        if i != 2:
            return
        log.info('DKIM rollover')
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            if 'handler' not in dkimContent:
                continue
            if 'rspamd' == dkimContent['handler']:
                log.info('using new dkim key, moving new config file')
                log.info('  {} -> {}'.format(dkimContent['signingconftemporaryfile'], dkimContent['signingconfdestinationfile']))
                rv = check_output(('mv', dkimContent['signingconftemporaryfile'], dkimContent['signingconfdestinationfile']))
                log.info('reloading rspamd')
                rv = check_output(('systemctl', 'reload', 'rspamd'))

    def dkimCleanup(self, i=2):
        if i != 2:
            return
        log.info('DKIM cleanup')
        for dkimSecName, dkimContent in self.cr.dkimconfig.items():
            if 'DEFAULT' == dkimSecName:
                continue
            if 'handler' not in dkimContent:
                continue
            if 'rspamd' == dkimContent['handler']:
                keyFiles = findDKIMkey(dkimContent['keylocation'], dkimContent['keybasename'])
                keyFiles.sort()
                if 2 > len(keyFiles):
                    return
                del keyFiles[-2:]
                for keyFile in keyFiles:
                    log.info('  rm {}'.format(keyFile[1]))
                    rv = check_output(('rm', keyFile[1]))
                self.setDKIM()

    def certPrepare(self, i=2):
        if i != 2:
            return
        log.info('Certificate prepare')
        self.stop80()
        createCert(self.cr.config)
        self.start80()

    def certRollover(self, i=2):
        if i != 2:
            return
        log.info('Certificate rollover')
        copyCert(self.cr.config)

    def certCleanup(self, i=2):
        if i != 2:
            return
        log.info('Certificate cleanup')

    def domainPrepare(self, i=8):
        if i != 8:
            return
        log.info('Domain prepare')
        self.addTLSA()

    def domainRollover(self, i=8):
        if i != 8:
            return
        log.info('Domain rollover')

    def domainCleanup(self, i=8):
        if i != 8:
            return
        log.info('Domain cleanup')
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
        for i in range(10):
            self.certPrepare(i)
            self.dkimPrepare(i)
            self.domainPrepare(i)

    def rollover(self, confFile = None):
        self.readConfig(confFile)
        for i in range(10):
            self.certRollover(i)
            self.dkimRollover(i)
            self.domainRollover(i)

    def cleanup(self, confFile = None):
        self.readConfig(confFile)
        for i in range(10):
            self.certCleanup(i)
            self.dkimCleanup(i)
            self.domainCleanup(i)




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






