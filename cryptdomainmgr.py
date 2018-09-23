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
#from modules.certificate.main import findCert
from modules.dkim.main import prepare as dkimPrepare
from modules.dkim.main import rollover as dkimRollover
from modules.dkim.main import cleanup as dkimCleanup
#from modules.dkim.handlerrspamd import findDKIMkeyTXT
from modules.service.main import prepare as serviceprepare
from modules.service.main import rollover as servicerollover
from modules.service.main import cleanup as servicecleanup
from modules.domain.main import prepare as domainPrepare
from modules.domain.main import rollover as domainRollover
from modules.domain.main import cleanup as domainCleanup
from modules.domain.main import update as domainUpdate

from simpleloggerplus import simpleloggerplus as log
from dnsuptools import dnsuptools 
from OpenSSL import crypto

def getCertSAN(filename):
    certFile = open(filename, 'rt').read()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certFile)
    san = [cert.get_extension(i).get_data().split('\x82')[1:] for i in range(cert.get_extension_count()) if 'subjectAltName' == cert.get_extension(i).get_short_name()][0]
    san = [e[1:] for e in san]
    return san

def getFullchain(state, domainContent):
    certState = state.getSubstate('cert').getSubstate(domainContent['certificate'])
    return certState.result['fullchainfile']

def isCertReady(state, domainContent):
    certState = state.getSubstate('cert').getSubstate(domainContent['certificate'])
    return 'done' == certState.opstate



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


    def update(self, state = '', confFile = None):
        self.readConfig(confFile)
        domainUpdate(self.cr.config, self.sh)
#        if 'prepare' == state:
#            self.addDKIM()
#            self.addTLSA()
#        elif 'cleanup' == state:
#            self.setDKIM()
#            self.setTLSA()

    def prepare(self, confFile = None):
        #self.sh.load()
        #self.sh.resetOpStateRecursive()
        self.readConfig(confFile)
        for i in range(10):
            certPrepare(self.cr.config, self.sh)
            dkimPrepare(self.cr.config, self.sh)
            domainPrepare(self.cr.config, self.sh)
            serviceprepare(self.cr.config, self.sh)
        self.sh.save()

    def rollover(self, confFile = None):
        self.sh.load()
        self.sh.resetOpStateRecursive()
        self.readConfig(confFile)
        for i in range(10):
            certRollover(self.cr.config, self.sh)
            dkimRollover(self.cr.config, self.sh)
            domainRollover(self.cr.config, self.sh)
            #servicerollover(self.cr.config, self.sh, i)
        self.sh.save()

    def cleanup(self, confFile = None):
        self.sh.load()
        self.sh.resetOpStateRecursive()
        self.readConfig(confFile)
        for i in range(10):
            certCleanup(self.cr.config, self.sh)
            dkimCleanup(self.cr.config, self.sh)
            domainCleanup(self.cr.config, self.sh)
            #servicecleanup(self.cr.config, self.sh, i)
        self.sh.save()







