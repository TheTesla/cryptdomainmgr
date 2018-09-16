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
from cdmstatehandler import *
from modules.certificate.main import prepare as certPrepare
from modules.certificate.main import rollover as certRollover
from modules.certificate.main import cleanup as certCleanup
from modules.certificate.main import findCert
from modules.dkim.main import prepare as dkimPrepare
from modules.dkim.main import rollover as dkimRollover
from modules.dkim.main import cleanup as dkimCleanup
from modules.dkim.handlerrspamd import findDKIMkeyTXT
from modules.service.main import prepare as serviceprepare
from modules.service.main import rollover as servicerollover
from modules.service.main import cleanup as servicecleanup

from simpleloggerplus import simpleloggerplus as log
from dnsuptools import dnsuptools 
from OpenSSL import crypto

def getCertSAN(filename):
    certFile = open(filename, 'rt').read()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certFile)
    san = [cert.get_extension(i).get_data().split('\x82')[1:] for i in range(cert.get_extension_count()) if 'subjectAltName' == cert.get_extension(i).get_short_name()][0]
    san = [e[1:] for e in san]
    return san

class ManagedDomain:
    def __init__(self):
        self.cr = ConfigReader()
        self.sh = StateHandler()
        self.dnsup = dnsuptools.DNSUpTools()
        self.confPar = configparser.ConfigParser()

    def readConfig(self, confFiles):
        self.cr.setFilenames(confFiles)
        self.cr.open()
        self.cr.interprete(self.sh)
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

    def setACME(self):
        for name, content in self.cr.config['domain'].items():
            if 'DEFAULT' == name:
                continue
            if 'acme' in content:
                print('acme')
                self.dnsup.setACME(name, content['acme'])

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
                certState = self.sh.getSubstate('cert').getSubstate(content['certificate'])
                #cert = findCert(name, content, self.cr.config)
                print(certState.result)
                cert = certState.result['fullchainfile']
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


    def addDKIM(self, delete = False):
        for dkimSecName, dkimContent in self.cr.config['dkim'].items():
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


    def domainPrepare(self, i=8):
        if i != 8:
            return
        log.info('Domain prepare')
        self.addTLSA()
        self.addDKIM()

    def domainRollover(self, i=8):
        if i != 8:
            return
        log.info('Domain rollover')

    def domainCleanup(self, i=8):
        if i != 8:
            return
        log.info('Domain cleanup')
        self.setTLSA()
        self.setDKIM()

    def domainUpdate(self):
        self.setACME()
        self.setCAA()
        self.setSOA()
        self.setSPF() # add and del entries
        self.setADSP()
        self.setDMARCentries()
        self.setSRV() # contains addSRV() and delSRV() 
        self.setIPs()
        self.setMX() # contains addMX() and delMX()


    def update(self, state = '', confFile = None):
        self.readConfig(confFile)
        self.domainUpdate()
        if 'prepare' == state:
            self.addDKIM()
            self.addTLSA()
        elif 'cleanup' == state:
            self.setDKIM()
            self.setTLSA()

    def prepare(self, confFile = None):
        self.readConfig(confFile)
        for i in range(10):
            certPrepare(self.cr.config, self.sh, i)
            print('blub')
            self.sh.printAll()
            print(self.sh.getSubstate('cert').getSubstate('maincert').result)
            dkimPrepare(self.cr.config, self.sh, i)
            self.domainPrepare(i)
            serviceprepare(self.cr.config, self.sh, i)

    def rollover(self, confFile = None):
        self.readConfig(confFile)
        for i in range(10):
            certRollover(self.cr.config, self.sh, i)
            dkimRollover(self.cr.config, self.sh, i)
            self.domainRollover(i)
            servicerollover(self.cr.config, self.sh, i)

    def cleanup(self, confFile = None):
        self.readConfig(confFile)
        for i in range(10):
            certCleanup(self.cr.config, self.sh, i)
            dkimCleanup(self.cr.config, self.sh, i)
            self.domainCleanup(i)
            servicecleanup(self.cr.config, self.sh, i)







