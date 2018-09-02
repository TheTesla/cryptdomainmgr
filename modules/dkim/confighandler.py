#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

def applyDefault(config, defaultConfig={}):
    default = dict(defaultConfig)
    if 'DEFAULT' in config:
        default.update(config['DEFAULT'])
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig


def interpreteDKIMConfig(cr):
    defaultDKIMConfig = {'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'signingconftemporaryfile': '/etc/rspamd/dkim_signing_new.conf', 'signingconftemplatefile': '/etc/rspamd/local.d/dkim_signing.conf'}
    dkimconfig = cr.getRawConfigOf('dkim')
    # apply general config defaults and the default section
    dkimconfig = applyDefault(dkimconfig, defaultDKIMConfig) # must be here because following section depends on default values
    cr.updateConfig({'dkim': dkimconfig})
    return dkimconfig


