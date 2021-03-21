#!/usr/bin/env python
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

# maybe this is never read - ToDo check this
#def interpreteConfig(cr, sh):
#    defaultServiceConfig = {'cert': 'auto', 'dkim': 'auto', 'dhparam': 'auto'}
#    serviceConfig = cr.getRawConfigOf('service')
#    log.debug(serviceConfig)
#    # apply general config defaults and the default section
#    serviceConfig = applyDefault(serviceConfig, defaultServiceConfig) # must be here because following section depends on default values
#    log.debug(serviceConfig)
#
#    for serviceSecName, content in serviceConfig.items():
#        content = dict(content)
#        for depends in ['cert', 'dkim', 'dhparam']:
#            if depends in content:
#                serviceConfig[serviceSecName][depends] = resolveAuto(cr, [e for e in content[depends].replace(' ', '').split(',') if len(e) > 0], depends)
#    log.debug(serviceConfig)
#    cr.updateConfig({'service': serviceConfig})
#    return serviceConfig
#
#def resolveAuto(configReader, serviceConfig, depends):
#    if 'auto' in serviceConfig:
#        dependKeys = configReader.getRawConfigOf(depends).keys()
#        serviceConfig.extend(dependKeys)
#        serviceConfig = [e for e in serviceConfig if e != 'auto' if e != 'DEFAULT']
#    return serviceConfig


def interpreteValues(args):
    for depends in ['cert', 'dkim', 'dhparam']:
        if depends in args['content']:
            args['config'][args['secname']][depends] = args['content'][depends].replace(' ','').split(',')



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


def interpreteConfig(cr, sh):
    return processConfig(cr, 'service', preOp=readHandlerDefault, postOp=interpreteValues, defaultConfig={'container': 'false', 'cert': 'auto', 'dkim': 'auto', 'dhparam': 'auto'})



