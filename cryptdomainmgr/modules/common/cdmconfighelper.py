#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from simpleloggerplus import simpleloggerplus as log

def applyDefault(config, defaultConfig={}, moduleName=None):
    config = applyInheritance(config, moduleName)
    default = dict(defaultConfig)
    if 'DEFAULT' in config:
        default.update(config['DEFAULT'])
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig


def applyInheritance(config, moduleName=None):
    # resolve 'inherit = <section>[,<section>...]' chains between named
    # sections, e.g. [cert:mail-smtp] inherit=cert:mail where
    # [cert:mail] itself inherits from the plain [cert] section.
    # References are written as in the config file: 'cert:mail' for a
    # named section, the bare module name ('cert') for the module base
    # section ([cert], stored as 'DEFAULT'). Multiple levels are
    # allowed, cycles raise an exception. The child's own keys win over
    # inherited ones.
    resolved = {}

    def resolve(secName, chain):
        # accept both the full section name as written in the config file
        # (e.g. 'cert:mail') and the module-internal key ('mail', the
        # '<module>:' prefix is stripped by the config reader)
        key = secName
        if key not in config and ':' in key:
            key = key.split(':', 1)[1]
        if key not in config and moduleName is not None and key == moduleName:
            key = 'DEFAULT'  # bare module name references the base section
        if key in resolved:
            return resolved[key]
        if key not in config:
            raise KeyError('inherit reference "{}" does not exist'.format(secName))
        if key in chain:
            raise ValueError('inherit cycle detected: {} -> {}'.format(' -> '.join(chain), key))
        content = dict(config[key])
        parents = []
        if 'inherit' in content:
            parents = [p.strip() for p in content['inherit'].split(',') if p.strip()]
            del content['inherit']
        merged = {}
        for parent in parents:
            parentContent = resolve(parent, chain + [key])
            merged.update(parentContent)
        merged.update(content)
        resolved[key] = merged
        return merged

    return {secName: resolve(secName, []) for secName in config}

def getStateDir(config, section=None, handler=None):
    statedir = config['cdm']['DEFAULT']['statedir']
    statedir = os.path.join(statedir, 'modules')
    if section is not None:
        statedir = os.path.join(statedir, '{}'.format(section))
    if handler is not None:
        statedir = os.path.join(statedir, '{}'.format(handler))
    return statedir

def readHandlerDefault(args):
    if 'handler' in args['content']:
        log.debug('handler in content')
        handlerNames = args['content']['handler'].split('/')
        try:
            handler = __import__('cryptdomainmgr.modules.{}.handler{}'.format(str(args['module']), handlerNames[0]), fromlist=('cryptdomainmgr', 'modules', str(args['module'])))
        except ImportError:
            # unknown handler: no handler defaults available, the module
            # specific dispatch applies its fallback (e.g. cert -> acme)
            log.warn('handler "{}" of module "{}" not available, no handler defaults applied'.format(handlerNames[0], args['module']))
            return
        args['config'][args['secname']].update(handler.defaultConfig)

def processConfig(configReader, module, postOp=None, preOp=readHandlerDefault, defaultConfig={}):
    configOrig = configReader.getRawConfigOf(str(module))
    # apply general config defaults and the default section
    config = applyDefault(configOrig, defaultConfig, moduleName=str(module)) # must be here because following section depends on default values
    # inherited raw values, resolved separately: the handler defaults
    # (preOp) rank BELOW inherited values, so they are re-asserted after
    # the preOp step (own section values rank highest and are applied
    # last, as before)
    inherited = applyInheritance(configOrig, moduleName=str(module))
    log.debug(config)
    for secName, content in config.items():
        if preOp is not None:
            preOp({'content': dict(content), 'module': str(module), 'config': config, 'secname': str(secName)})
        config[secName].update(inherited[secName])
        config[secName].update(configOrig[secName])
        config[secName].pop('inherit', None)  # consumed by the resolution
        if postOp is not None:
            postOp({'content': dict(content), 'module': str(module), 'config': config, 'secname': str(secName)})
    log.debug(config)
    configReader.updateConfig({str(module): config})
    return config

