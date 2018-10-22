#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.modules.common.cdmconfighelper import applyDefault
from simpleloggerplus import simpleloggerplus as log


# Default handling
# DEFAULT section overwritten by handler default configuration overwr. by explicit configuration


def interpreteConfig(cr, sh):
    defaultServiceConfig = {'cert': 'auto', 'dkim': 'auto'}
    serviceConfig = cr.getRawConfigOf('service')
    log.debug(serviceConfig)
    # apply general config defaults and the default section
    serviceConfig = applyDefault(serviceConfig, defaultServiceConfig) # must be here because following section depends on default values
    log.debug(serviceConfig)

    for serviceSecName, content in serviceConfig.items():
        content = dict(content)
        for depends in ['cert', 'dkim']:
            if depends in content:
                serviceConfig[serviceSecName][depends] = [e for e in content[depends].replace(' ', '').split(',') if len(e) > 0]
    log.debug(serviceConfig)
    cr.updateConfig({'service': serviceConfig})
    return serviceConfig

