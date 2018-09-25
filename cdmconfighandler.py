#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import configparser

from simpleloggerplus import simpleloggerplus as log
#from modules.certificate.confighandler import interpreteConfig as interpreteCertConfig
#from modules.dkim.confighandler import interpreteConfig as interpreteDKIMConfig
#from modules.domain.confighandler import interpreteConfig as interpreteDomainConfig
#from modules.service.confighandler import interpreteConfig as interpreteServiceConfig

class ConfigReader:
    def __init__(self):
        self.cp = configparser.ConfigParser()
        self.filenameList = []
        self.conflictingservices = {}
        self.config = {}

    def setFilenames(self, filenames):
        if filenames is None:
            return
        if type(filenames) is str:
            filenames = [filenames]
        self.filenameList = filenames

    def addFilenames(self, filenames):
        if filenames is None:
            return
        if type(filenames) is str:
            filenames = [filenames]
        self.filenameList.extend(filenames)

    def open(self):
        self.cp = configparser.ConfigParser()
        self.cp.read(self.filenameList)

    def getRawConfigOf(self, getSection, domainOldStyle=False):
        return getConfigOf(getSection, self.cp, domainOldStyle)

    def updateConfig(self, config):
        self.config.update(config)

    def interprete(self, sh):
        self.sections = getSections(self.cp)
        log.info('Interpreting config sections')
        for secName in self.sections:
            log.info('  - {}'.format(secName))
            handler = __import__('modules.'+str(secName)+'.confighandler', fromlist=('modules'))
            handler.interpreteConfig(self, sh)
        #interpreteDomainConfig(self, sh)
        #interpreteCertConfig(self, sh)
        #interpreteDKIMConfig(self, sh)
        #interpreteServiceConfig(self, sh)
        log.debug(self.config)

def getSections(config):
    return set([k.split(':')[0] for k, v in config.items() if k != 'DEFAULT'])
    

def getConfigOf(getSection, config, domainOldStyle=False):
    resConfig = {}
    for name, content in config.items():
        section = name.split(':')
        if getSection != section[0]:
            if domainOldStyle is True:
                if '.' not in section[0]: # fallback if not domain:example.de but example.de
                    continue
            else:
                continue
        if 2 == len(section):
            secName = section[1]
        else:
            secName = 'DEFAULT'
            if domainOldStyle is True:
                if '.' in section[0]:
                    secName = section[0] # fallback if not domain:example.de but example.de
        resConfig[secName] = dict({str(k): str(v) for k, v in content.items()})
    return resConfig

