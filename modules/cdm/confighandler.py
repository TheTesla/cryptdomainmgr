#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from ..common.cdmconfighelper import applyDefault

def interpreteConfig(cr, sh):
    defaultCDMConfig = {'statedir': '/var/cryptdomainmgr'}
    cdmConfig = cr.getRawConfigOf('cdm')
    # apply general config defaults and the default section
    cdmConfig = applyDefault(cdmConfig, defaultCDMConfig) # must be here because following section depends on default values
    cr.updateConfig({'cdm': cdmConfig['DEFAULT']})
    return cdmConfig

