#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.modules.common.cdmconfighelper import processConfig
from cryptdomainmgr.modules.common.cdmconfighelper import applyDefault

def resolveAuto(serviceConfig, dependSections):
    if 'auto' in serviceConfig:
        serviceConfig.extend(dependSections)
    serviceConfig = [e for e in serviceConfig if e != 'auto' and e !='DEFAULT']
    serviceConfig = list(set(serviceConfig))
    return serviceConfig


def interpreteValues(cr, args):
    depends = args['content']['depends'].replace(' ','').split(',')
    args['config'][args['secname']]['depends'] = list(set(depends)) #if 0 < len(depends[0]) else []
    for depend in depends:
        dependSections = cr.getRawConfigOf(depend).keys()
        if depend in args['content']:
            dependVals = args['content'][depend].replace(' ','').split(',')
            dependsResolved = resolveAuto(dependVals,dependSections)
            args['config'][args['secname']][depend] = dependsResolved
            if len(dependsResolved) > len(dependSections):
                log.warn("Dependency in config entry does not exist!")



def interpreteConfig(cr, sh):
    cnf =  processConfig(cr, 'cdm', preOp=None, postOp=lambda x:  interpreteValues(cr, x),
                         defaultConfig={'statedir': '/var/cryptdomainmgr',
                                        'depends': 'cert, domain, dkim, \
                                        dhparam, service'})
    return cnf


#def interpreteConfig(cr, sh):
#    defaultCDMConfig = {'statedir': '/var/cryptdomainmgr'}
#    cdmConfig = cr.getRawConfigOf('cdm')
#    # apply general config defaults and the default section
#    cdmConfig = applyDefault(cdmConfig, defaultCDMConfig) # must be here because following section depends on default values
#    cr.updateConfig({'cdm': cdmConfig['DEFAULT']})
#    return cdmConfig
#


