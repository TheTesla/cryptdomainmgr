#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr.modules.common.cdmconfighelper import processConfig

# the bundled dehydrated was removed from the project; legacy
# dehydrated handler configurations are served by the acme handler
STAGINGCA = 'https://acme-staging-v02.api.letsencrypt.org/directory'


# Default handling
# DEFAULT section overwritten by handler default configuration overwr. by explicit configuration

def interpreteValues(args):
    content = args['content']
    certconfig = args['config']
    certSecName = args['secname']
    handlerNames = content['handler'].split('/')
    if 'keysize' in content:
        certconfig[certSecName]['keysize'] = int(content['keysize'])
    extraflags = [e for e in str(content.get('extraflags', '')).replace(' ', '').split(',') if len(e) > 0]
    if 'dehydrated' == handlerNames[0]:
        certconfig[certSecName]['handler'] = 'acme'
        # dehydrated's --staging extra flag maps to the letsencrypt
        # staging CA directory
        if 'staging' in [e.lstrip('-') for e in extraflags] and 'ca' not in content:
            certconfig[certSecName]['ca'] = STAGINGCA
        extraflags = [e for e in extraflags if 'staging' != e.lstrip('-')]
    if 1 < len(handlerNames):
        if 'letsencrypt' != handlerNames[1]:
            certconfig[certSecName]['caa'] = ''
    certconfig[certSecName]['extraflags'] = extraflags

def interpreteConfig(cr, sh):
    return processConfig(cr, 'cert', postOp=interpreteValues, defaultConfig={'handler': 'acme', 'keysize': 4096, 'extraflags': '', 'caa': {'url': 'letsencrypt.org', 'flag': '0', 'tag': 'issue'}})
