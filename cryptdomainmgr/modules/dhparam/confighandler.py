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


def interpreteValues(args):
    if 'keysize' in args['content']:
        args['config'][args['secname']]['keysize'] = int(args['content']['keysize'])

def interpreteConfig(cr, sh):
    return processConfig(cr, 'dhparam', postOp=interpreteValues, defaultConfig={'filename': '/etc/myssl/dhparam.pem', 'keysize': 2048})

