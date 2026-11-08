#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# rspamd dkim key handler: generates the key pair with rspamadm and
# deploys it with _rspamd ownership at rollover. The rspamd signing
# config rendering is done by the rspamd SERVICE handler
# (modules/service/handlerrspamd.py), this handler only provides the
# key.

import os
from subprocess import check_output, CalledProcessError
from simpleloggerplus import simpleloggerplus as log
import time
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir

defaultConfig = {'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'keyname': 'dkim.key'}

def prepare(dkimConfig, dkimState, statedir):
    if 'rspamd' == dkimConfig['handler'].split('/')[0]:
        res = createDKIM(dkimConfig['keysize'], os.path.join(statedir, 'key', 'dkim.key'))
        res['keyname'] = createSelector(dkimConfig['keybasename'])
        dkimState.registerResult(res)
        dkimState.setOpStateDone()

def rollover(dkimConfig, dkimState):
    if 'rspamd' == dkimConfig['handler'].split('/')[0]:
        log.info('using new dkim key, moving new key file')
        copyDKIM(dkimConfig, dkimState)
        dkimState.setOpStateDone()

def cleanup(dkimConfig, dkimState):
    if 'rspamd' == dkimConfig['handler'].split('/')[0]:
        dkimState.setOpStateDone()

def copyDKIM(dkimConfig, dkimState):
    src = dkimState.result['keyfile']
    dest = os.path.join(dkimConfig['keylocation'], dkimConfig['keyname'])
    log.info('  {} -> {}'.format(src, dest))
    try:
        rv = check_output(('mkdir', '-p', os.path.dirname(str(dest))))
    except CalledProcessError as e:
        log.error("Failed to create directory path for {}".format(str(dest)))
    try:
        rv = check_output(('sudo', 'cp', '-rfLT', str(src), str(dest)))
    except CalledProcessError as e:
        log.error("Failed to copy file")
        log.error("  {} -> {}".format(str(src), str(dest)))
    try:
        rv = check_output(('sudo', 'chown', '_rspamd:_rspamd', str(dest)))
    except CalledProcessError as e:
        log.error("Failed to change ownership of {}".format(str(dest)))

def createSelector(keybasename):
    return str(keybasename) + '_{:10d}'.format(int(time.time()))

def createDKIM(keysize, destination):
    makeDir(os.path.dirname(str(destination)))
    try:
        keyTxt = str(check_output(('sudo', 'rspamadm', 'dkim_keygen', '-b', str(int(keysize)), '-s', str('dkimkey'), '-k', str(destination))))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)
    v = keyTxt.split('v=')[1].split(';')[0]
    k = keyTxt.split('k=')[1].split(';')[0]
    pL = keyTxt.split('p=')[1].split('\"')
    p = "".join([e for e in pL if ")" not in e and "\n" not in e])
    p = p.replace("\\n", "").replace("\\t", "")
    return {'v': v, 'k': k, 'p': p, 'keyfile': str(destination)}
