#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.modules.common.cdmconfighelper import processConfig
from cryptdomainmgr.modules.common.cdmconfighelper import applyDefault
from simpleloggerplus import simpleloggerplus as log


# Default handling
# DEFAULT section overwritten by handler default configuration overwr. by explicit configuration

def resolveAuto(config, serviceConfig, depends):
    if 'auto' in serviceConfig:
        log.debug("This will never be called!")
        if depends not in config:
            return []
        dependKeys = config[depends]
        serviceConfig.extend(dependKeys)
        serviceConfig = [e for e in serviceConfig if e != 'auto' if e != 'DEFAULT']
    return serviceConfig


def interpreteValues(args):
    depends = args['content']['depends'].replace(' ','').split(',')
    args['config'][args['secname']]['depends'] = set(depends) if 0 < len(depends[0]) else {}
    for depend in depends:
        if depend in args['content']:
            args['config'][args['secname']][depend] = resolveAuto(args['config'], args['content'][depend].replace(' ','').split(','), depend)



def readHandlerDefault(args):
    handlerName = ''
    if 'handler' not in args['content']:
        handlerName = 'auto'
    else:
        handlerName = args['content']['handler']
    if 'auto' == handlerName:
        handlerName = args['secname']
    if 'DEFAULT' == args['secname']:
        return
    handlerNames = handlerName.split('/')
    handler = __import__('cryptdomainmgr.modules.{}.handler{}'.format(str(args['module']), handlerNames[0]), fromlist=('cryptdomainmgr', 'modules', str(args['module'])))
    args['config'][args['secname']].update(handler.defaultConfig)
    args['config'][args['secname']].update({'handler': handlerName})


def interpreteConfig(cr, sh):
    return processConfig(cr, 'service', preOp=readHandlerDefault, postOp=interpreteValues, defaultConfig={'container': 'false', 'depends': ''})




