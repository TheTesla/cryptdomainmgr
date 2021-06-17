#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.modules.common.cdmconfighelper import processConfig


# Default handling
# DEFAULT section overwritten by handler default configuration overwr. by explicit configuration

def interpreteValues(args):
    content = args['content']
    certconfig = args['config']
    certSecName = args['secname']
    handlerNames = content['handler'].split('/')
    if 1 < len(handlerNames):
        if 'letsencrypt' != handlerNames[1]:
            certconfig[certSecName]['caa'] = ''
    if 'keysize' in content:
        certconfig[certSecName]['keysize'] = int(content['keysize'])
    if 'extraflags' in content:
        certconfig[certSecName]['extraflags'] = [e for e in content['extraflags'].replace(' ', '').split(',') if len(e) > 0]

def interpreteConfig(cr, sh):
    return processConfig(cr, 'cert', postOp=interpreteValues, defaultConfig={'handler': 'dehydrated/letsencrypt', 'keysize': 4096, 'extraflags': ''})

