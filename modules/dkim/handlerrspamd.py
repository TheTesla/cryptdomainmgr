#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from subprocess import check_output
from simpleloggerplus import simpleloggerplus as log
from jinja2 import Template
from parse import parse
import time
from ..common.cdmfilehelper import makeDir

here = os.path.dirname(os.path.realpath(__file__))
defaultDKIMConfig = {'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'signingconftemporaryfile': '/etc/rspamd/dkim_signing_new.conf', 'signingconfdestinationfile': '/etc/rspamd/local.d/dkim_signing.conf', 'signingconftemplatefile': os.path.join(here, 'dkim_signing_template.conf')}

def prepare(dkimConfig, dkimState):
    if 'rspamd' == dkimConfig['handler']:
        res = createDKIM(dkimConfig['keylocation'], dkimConfig['keybasename'], dkimConfig['keysize'], dkimConfig['signingconftemplatefile'], dkimConfig['signingconftemporaryfile'])
        dkimState.registerResult(res)
        dkimState.setOpStateDone()

def rollover(dkimConfig, dkimState):
    if 'rspamd' == dkimConfig['handler']:
        log.info('using new dkim key, moving new config file')
        log.info('  {} -> {}'.format(dkimConfig['signingconftemporaryfile'], dkimConfig['signingconfdestinationfile']))
        rv = check_output(('mv', dkimConfig['signingconftemporaryfile'], dkimConfig['signingconfdestinationfile']))
        dkimState.setOpStateDone()

def cleanup(dkimConfig, dkimState):
    if 'rspamd' == dkimConfig['handler']:
        keyFiles = findDKIMkey(dkimConfig['keylocation'], dkimConfig['keybasename'])
        keyFiles.sort()
        if 2 > len(keyFiles):
            return
        del keyFiles[-2:]
        for keyFile in keyFiles:
            log.info('  rm {}'.format(keyFile[1]))
            rv = check_output(('rm', keyFile[1]))
        dkimState.setOpStateDone()

def createDKIM(keylocation, keybasename, keysize, signingConfTemplateFile, signingConfDestFile):
    keylocation = os.path.expanduser(keylocation)
    newKeyname = str(keybasename) + '_{:10d}'.format(int(time.time()))
    log.info('  -> {}'.format(newKeyname))
    makeDir(keylocation)
    keyTxt = check_output(('rspamadm', 'dkim_keygen', '-b', str(int(keysize)), '-s', str(newKeyname), '-k', os.path.join(keylocation, newKeyname+'.key')))
    keyPath = os.path.join(keylocation, newKeyname)
    f = open(keyPath+'.txt', 'w')
    f.write(keyTxt)
    f.close()
    rv = check_output(('chmod', '0440', keyPath+'.key'))
    rv = check_output(('chown', '_rspamd:_rspamd', keyPath+'.key'))
    f = open(os.path.expanduser(signingConfTemplateFile), 'r')
    templateContent = f.read()
    f.close()
    template = Template(templateContent)
    confDestContent = template.render(keyname = newKeyname, keylocation = keylocation)
    f = open(os.path.expanduser(signingConfDestFile), 'w')
    f.write(confDestContent)
    f.close()
    return {'keytxtfile': keyPath+'.txt', 'keyfile': keyPath+'.key', 'keybasename': str(keybasename), 'keyname': str(newKeyname)}

def findDKIMkeyTXT(keylocation, keybasename, fileending = 'txt'):
    return findDKIMkey(keylocation, keybasename, fileending)

def findDKIMkey(keylocation, keybasename, fileending = '{}'):
    keylocation = os.path.expanduser(keylocation)
    keyfiles = [(parse(str(keybasename)+'_{:d}.'+str(fileending), f), os.path.join(keylocation, f)) for f in os.listdir(keylocation) if os.path.isfile(os.path.join(keylocation, f))]
    log.debug(keyfiles)
    keyfiles = [(e[0][0], e[1]) for e in keyfiles if e[0] is not None]
    log.debug(keyfiles)
    return keyfiles

