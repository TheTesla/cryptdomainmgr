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
    defaultDHparamConfig = {'filename': '/etc/myssl/dhparam.pem', 'keysize': 2048}
    dhparamconfigOrig = cr.getRawConfigOf('dhparam')
    # apply general config defaults and the default section
    dhparamconfig = applyDefault(dhparamconfigOrig, defaultDHparamConfig) # must be here because following section depends on default values

    log.debug(dhparamconfig)
    for dhparamSecName, content in dhparamconfig.items():
        content = dict(content)
        if 'handler' in content:
            log.debug('handler in content')
            handlerNames = content['handler'].split('/')
            handler = __import__('cryptdomainmgr.modules.dhparam.handler'+str(handlerNames[0]), fromlist=('cryptdomainmgr','modules','dhparam'))
            log.debug(dhparamconfig)
            dhparamconfig[dhparamSecName].update(handler.defaultDHparamConfig)
            log.debug(dhparamconfig)
            dhparamconfig[dhparamSecName].update(dhparamconfigOrig[dhparamSecName])
            log.debug(dhparamconfig)
        if 'keysize' in content:
            dhparamconfig[dhparamSecName]['keysize'] = int(content['keysize'])
    log.debug(dhparamconfig)
    cr.updateConfig({'dhparam': dhparamconfig})
    return dhparamconfig

