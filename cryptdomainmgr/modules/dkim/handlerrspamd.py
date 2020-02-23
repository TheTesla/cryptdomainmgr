#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from subprocess import check_output, CalledProcessError
from simpleloggerplus import simpleloggerplus as log
from jinja2 import Template
from parse import parse
import time
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir

here = os.path.dirname(os.path.realpath(__file__))
defaultConfig = {'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'keyname': 'dkim.key', 'signingconfdestinationfile': '/etc/rspamd/local.d/dkim_signing.conf', 'signingconftemplatefile': os.path.join(here, 'dkim_signing_template.conf')}

def prepare(dkimConfig, dkimState, statedir):
    if 'rspamd' == dkimConfig['handler'].split('/')[0]:
        res = createDKIM(dkimConfig['keysize'], os.path.join(statedir, 'key', 'dkim.key'))
        keySelector = createSelector(dkimConfig['keybasename'])
        u = createConf(dkimConfig['signingconftemplatefile'], os.path.join(statedir, 'conf', 'dkim.conf'), os.path.join(dkimConfig['keylocation'], dkimConfig['keyname']), keySelector)
        res.update(u)
        dkimState.registerResult(res)
        dkimState.setOpStateDone()

def rollover(dkimConfig, dkimState):
    if 'rspamd' == dkimConfig['handler'].split('/')[0]: 
        log.info('using new dkim key, moving new config file')
        copyDKIM(dkimConfig, dkimState)
        copyConf(dkimConfig, dkimState)
        dkimState.setOpStateDone()

def cleanup(dkimConfig, dkimState):
    if 'rspamd' == dkimConfig['handler'].split('/')[0]:
        dkimState.setOpStateDone()

def copyDKIM(dkimConfig, dkimState):
    src = dkimState.result['keyfile']
    dest = os.path.join(dkimConfig['keylocation'], dkimConfig['keyname'])
    log.info('  {} -> {}'.format(src, dest))
    try:
        rv = check_output(('cp', '-rfLT', str(src), str(dest)))
        rv = check_output(('chown', '_rspamd:_rspamd', str(dest)))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)

def copyConf(dkimConfig, dkimState):
    src = dkimState.result['signingconftemporaryfile']
    dest = dkimConfig['signingconfdestinationfile']
    log.info('  {} -> {}'.format(src, dest))
    try:
        rv = check_output(('cp', '-rfLT', str(src), str(dest)))
        rv = check_output(('chown', '_rspamd:_rspamd', str(dest)))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)

def createSelector(keybasename):
    return str(keybasename) + '_{:10d}'.format(int(time.time()))

def createDKIM(keysize, destination):
    makeDir(os.path.dirname(str(destination)))
    try:
        keyTxt = str(check_output(('rspamadm', 'dkim_keygen', '-b', str(int(keysize)), '-s', str('dkimkey'), '-k', str(destination))))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)
    v = keyTxt.split('v=')[1].split(';')[0]
    k = keyTxt.split('k=')[1].split(';')[0]
    pL = keyTxt.split('p=')[1].split('\"')
    p = "".join([e for e in pL if ")" not in e and "\n" not in e])
    return {'v': v, 'k': k, 'p': p, 'keyfile': str(destination)}


def createConf(signingConfTemplateFile, signingConfDestFile, keyFile, keySelector):
    f = open(os.path.expanduser(signingConfTemplateFile), 'r')
    templateContent = f.read()
    f.close()
    template = Template(templateContent)
    confDestContent = str(template.render(keyselector=keySelector, keyfile=keyFile))
    makeDir(os.path.dirname(str(signingConfDestFile)))
    f = open(os.path.expanduser(signingConfDestFile), 'w')
    f.write(confDestContent)
    f.close()
    return {'signingconftemporaryfile': signingConfDestFile, 'keyname': keySelector}


