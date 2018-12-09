#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from simpleloggerplus import simpleloggerplus as log

def applyDefault(config, defaultConfig={}):
    default = dict(defaultConfig)
    if 'DEFAULT' in config:
        default.update(config['DEFAULT'])
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig

def getStateDir(config, section=None, handler=None):
    statedir = config['cdm']['statedir']
    statedir = os.path.join(statedir, 'modules')
    if section is not None:
        statedir = os.path.join(statedir, '{}'.format(section))
    if handler is not None:
        statedir = os.path.join(statedir, '{}'.format(handler))
    return statedir

def readHandlerDefault(args):
    if 'handler' in args['content']:
        log.debug('handler in content')
        handlerNames = args['content']['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.{}.handler{}'.format(str(args['module']), handlerNames[0]), fromlist=('cryptdomainmgr', 'modules', str(args['module'])))
        args['config'][args['secname']].update(handler.defaultConfig)

def processConfig(configReader, module, postOp=None, preOp=readHandlerDefault, defaultConfig={}):
    configOrig = configReader.getRawConfigOf(str(module))
    # apply general config defaults and the default section
    config = applyDefault(configOrig, defaultConfig) # must be here because following section depends on default values
    log.debug(config)
    for secName, content in config.items():
        if preOp is not None:
            preOp({'content': dict(content), 'module': str(module), 'config': config, 'secname': str(secName)})
        config[secName].update(configOrig[secName])
        if postOp is not None:
            postOp({'content': dict(content), 'module': str(module), 'config': config, 'secname': str(secName)})
    log.debug(config)
    configReader.updateConfig({str(module): config})
    return config

