#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# OpenDKIM service handler: generates the KeyTable/SigningTable entries
# for the domains referencing a prepared dkim section and reloads
# opendkim. The dkim section (e.g. handler=openssl) only provides the
# key file and the selector - the domain-to-dkim mapping comes from the
# domain sections (dkim.<dkimSecName>=auto), same pattern as
# handlertraefik resolving its cert references.

import os
from simpleloggerplus import simpleloggerplus as log
from cryptdomainmgr.modules.common.cdmstatehelper import isReady
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir
from cryptdomainmgr.modules.service.servicehelper import reloadService

defaultConfig = {'depends': 'dkim', 'dkim': 'auto', 'keytablefile': '/etc/opendkim/KeyTable', 'signingtablefile': '/etc/opendkim/SigningTable', 'reload': 'true'}


def getDKIMDomains(config, dkimSecName):
    """Domains whose dkim section references dkimSecName, resolved from
    the domain sections (dkimAggrAdd contains the referenced dkim section
    names with op=auto)."""
    domains = []
    for domainSecName, domainConfig in config['domain'].items():
        if 'DEFAULT' == domainSecName:
            continue
        for e in domainConfig.get('dkimAggrAdd', []):
            if e.get('content') == dkimSecName:
                domains.append(domainSecName)
                break
    return domains


def writeTable(filename, lines):
    makeDir(os.path.dirname(filename))
    with open(filename, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    log.info('  wrote {} ({} entries)'.format(filename, len(lines)))


def rollover(serviceConfig, serviceState, state, config):
    serviceState.setOpStateWaiting()
    if not isReady(serviceConfig, state, 'dkim'):
        return
    serviceState.setOpStateRunning()
    dkimSecName = serviceConfig['dkim'][0]
    dkimState = state.getSubstate('dkim').getSubstate(dkimSecName)
    selector = dkimState.result['keyname']
    # opendkim reads the key from the deployed location (keylocation/
    # keyname from the dkim section config), not the staging path
    dkimConfig = config['dkim'][dkimSecName]
    keyfile = os.path.join(dkimConfig['keylocation'], dkimConfig['keyname'])

    keytableLines = []
    signingtableLines = []
    for domain in getDKIMDomains(config, dkimSecName):
        dkimDomain = '{}._domainkey.{}'.format(selector, domain)
        keytableLines.append('{} {}:{}'.format(dkimDomain, domain, selector))
        keytableLines[-1] += ':' + keyfile
        signingtableLines.append('*@{} {}'.format(domain, dkimDomain))
        log.info('  signing domain {} with selector {} (key {})'.format(domain, selector, keyfile))

    writeTable(serviceConfig['keytablefile'], keytableLines)
    writeTable(serviceConfig['signingtablefile'], signingtableLines)

    if 'true' == str(serviceConfig.get('reload', 'true')):
        log.info('  -> OpenDKIM reload')
        try:
            reloadService('opendkim')
        except Exception as e:
            log.error('opendkim reload failed: {}'.format(e))
            raise(e)
    else:
        log.info('  -> OpenDKIM reload disabled by config')
    serviceState.setOpStateDone()

def prepare(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()
