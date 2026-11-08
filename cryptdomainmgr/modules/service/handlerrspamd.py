#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# rspamd service handler: renders the rspamd dkim signing config
# (path + selector) from the dkim section result and reloads rspamd.
# The signing config is rspamd-specific knowledge and therefore lives
# here, not in the dkim module - the dkim handlers only provide the key
# and the selector.

import os
from jinja2 import Template
from simpleloggerplus import simpleloggerplus as log
from cryptdomainmgr.modules.common.cdmstatehelper import isReady
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir
from cryptdomainmgr.modules.service.servicehelper import reloadService

here = os.path.dirname(os.path.realpath(__file__))
defaultConfig = {'depends': 'dkim', 'dkim': 'auto', 'reload': 'true',
                 'signingconfdestinationfile': '/etc/rspamd/local.d/dkim_signing.conf',
                 'signingconftemplatefile': os.path.join(here, 'dkim_signing_template.conf')}


def prepare(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

def rollover(serviceConfig, serviceState, state, config):
    serviceState.setOpStateWaiting()
    if not isReady(serviceConfig, state, 'dkim'):
        return
    serviceState.setOpStateRunning()
    dkimSecName = serviceConfig['dkim'][0]
    dkimState = state.getSubstate('dkim').getSubstate(dkimSecName)
    selector = dkimState.result['keyname']
    # rspamd reads the key from the deployed location (keylocation/
    # keyname from the dkim section config)
    dkimConfig = config['dkim'][dkimSecName]
    keyfile = os.path.join(dkimConfig['keylocation'], dkimConfig['keyname'])

    with open(serviceConfig['signingconftemplatefile'], 'r') as f:
        template = Template(f.read())
    confContent = template.render(keyselector=selector, keyfile=keyfile)
    makeDir(str(os.path.dirname(serviceConfig['signingconfdestinationfile'])))
    with open(serviceConfig['signingconfdestinationfile'], 'w') as f:
        f.write(confContent)
    log.info('  wrote {} (selector {})'.format(serviceConfig['signingconfdestinationfile'], selector))

    if 'true' == str(serviceConfig.get('reload', 'true')):
        log.info('  -> Rspamd reload')
        try:
            reloadService('rspamd')
        except Exception as e:
            log.error('rspamd reload failed: {}'.format(e))
            raise(e)
    else:
        log.info('  -> Rspamd reload disabled by config')
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()
