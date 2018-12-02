#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os

def applyDefault(config, defaultConfig={}):
    default = dict(defaultConfig)
    if 'DEFAULT' in config:
        default.update(config['DEFAULT'])
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig

def getStateDir(config, section=None, handler=None):
    statedir = config['cdm']['statedir']
    statedir = os.path.join(statedir, 'modules')
    if section is not None:
        statedir = os.path.join(statedir, '{}'.format(section))
    if handler is not None:
        statedir = os.path.join(statedir, '{}'.format(handler))
    return statedir

