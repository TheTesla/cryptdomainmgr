#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


from subprocess import check_output
import os
import time
from cdmconfighandler import *
from cdmstatehandler import *
from modules.certificate.main import prepare as certPrepare
from modules.certificate.main import rollover as certRollover
from modules.certificate.main import cleanup as certCleanup
from modules.dkim.main import prepare as dkimPrepare
from modules.dkim.main import rollover as dkimRollover
from modules.dkim.main import cleanup as dkimCleanup
from modules.service.main import prepare as servicePrepare
from modules.service.main import rollover as serviceRollover
from modules.service.main import cleanup as serviceCleanup
from modules.domain.main import prepare as domainPrepare
from modules.domain.main import rollover as domainRollover
from modules.domain.main import cleanup as domainCleanup
from modules.domain.main import update as domainUpdate

from simpleloggerplus import simpleloggerplus as log

class ManagedDomain:
    def __init__(self):
        self.cr = ConfigReader()
        self.sh = StateHandler()

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
            servicePrepare(self.cr.config, self.sh)
        self.sh.save()

    def rollover(self, confFile = None):
        self.sh.load()
        self.sh.resetOpStateRecursive()
        self.readConfig(confFile)
        for i in range(10):
            certRollover(self.cr.config, self.sh)
            dkimRollover(self.cr.config, self.sh)
            domainRollover(self.cr.config, self.sh)
            serviceRollover(self.cr.config, self.sh)
        self.sh.save()

    def cleanup(self, confFile = None):
        self.sh.load()
        self.sh.resetOpStateRecursive()
        self.readConfig(confFile)
        for i in range(10):
            certCleanup(self.cr.config, self.sh)
            dkimCleanup(self.cr.config, self.sh)
            domainCleanup(self.cr.config, self.sh)
            serviceCleanup(self.cr.config, self.sh)
        self.sh.save()







