#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

def applyDefault(config, defaultConfig={}):
    default = dict(defaultConfig)
    if 'DEFAULT' in config:
        default.update(config['DEFAULT'])
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig

# Default handling
# DEFAULT section overwritten by handler default configuration overwr. by explicit configuration

def interpreteConfig(cr, sh):
    defaultDKIMConfig = {'keysize': 2048, 'keybasename': 'key'}
    dkimconfig = cr.getRawConfigOf('dkim')
    # apply general config defaults and the default section
    dkimconfig = applyDefault(dkimconfig, defaultDKIMConfig) # must be here because following section depends on default values
    for dkimSecName, content in dkimconfig.items():
        content = dict(content)
        if 'handler' in content:
            handlerNames = content['handler'].split('/')
            handler = __import__('modules.dkim.handler'+str(handlerNames[0]), fromlist=('modules','dkim'))
            dkimconfig[dkimSecName].update(handler.defaultDKIMConfig)
            dkimconfig[dkimSecName].update(content)
    cr.updateConfig({'dkim': dkimconfig})
    return dkimconfig


