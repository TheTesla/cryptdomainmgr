#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.modules.common.cdmconfighelper import applyDefault, processConfig
from simpleloggerplus import simpleloggerplus as log


# Default handling
# DEFAULT section overwritten by handler default configuration overwr. by explicit configuration

def readHandlerDefault(args):
    if not 'keybasename' in args['content']:
        args['content']['keybasename'] = str(args['secname'])
    if 'handler' in args['content']:
        log.debug('handler in content')
        handlerNames = args['content']['handler'].split('/')
        handler = __import__('cryptdomainmgr.modules.{}.handler{}'.format(str(args['module']), handlerNames[0]), fromlist=('cryptdomainmgr', 'modules', str(args['module'])))
        args['config'][args['secname']].update(handler.defaultConfig)

def interpreteConfig(cr, sh):
    return processConfig(cr, 'dkim', preOp=readHandlerDefault, defaultConfig={'keysize': 2048})


