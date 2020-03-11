#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.modules.common.cdmconfighelper import applyDefault

def interpreteConfig(cr, sh):
    defaultTESTConfig = {'defaultx': '23', 'defaulty': '42'}
    testConfig = cr.getRawConfigOf('test')
    # apply general config defaults and the default section
    testConfig = applyDefault(testConfig, defaultTESTConfig) # must be here because following section depends on default values
    cr.updateConfig({'test': testConfig})
    return testConfig

