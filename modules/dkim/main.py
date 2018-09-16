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
import handlerrspamd

def prepare(config, state, i=2):
    if i != 2:
        return
    log.info('DKIM prepare')
    for dkimSecName, dkimContent in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        log.info("Preparing DKIM key for dkim-section: \"{}\"".format(dkimSecName))
        if 'handler' not in dkimContent:
            continue
        handlerrspamd.prepare(dkimContent, i)
#        if 'rspamd' == dkimContent['handler']:
#            createDKIM(dkimContent['keylocation'], dkimContent['keybasename'], dkimContent['keysize'], dkimContent['signingconftemplatefile'], dkimContent['signingconftemporaryfile'])

def rollover(config, state, i=2):
    if i != 2:
        return
    log.info('DKIM rollover')
    for dkimSecName, dkimContent in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        if 'handler' not in dkimContent:
            continue
        handlerrspamd.rollover(dkimContent, i)
#        if 'rspamd' == dkimContent['handler']:
#            log.info('using new dkim key, moving new config file')
#            log.info('  {} -> {}'.format(dkimContent['signingconftemporaryfile'], dkimContent['signingconfdestinationfile']))
#            rv = check_output(('mv', dkimContent['signingconftemporaryfile'], dkimContent['signingconfdestinationfile']))

def cleanup(config, state, i=2):
    if i != 2:
        return
    log.info('DKIM cleanup')
    for dkimSecName, dkimContent in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        if 'handler' not in dkimContent:
            continue
        handlerrspamd.cleanup(dkimContent, i)
#        if 'rspamd' == dkimContent['handler']:
#            keyFiles = findDKIMkey(dkimContent['keylocation'], dkimContent['keybasename'])
#            keyFiles.sort()
#            if 2 > len(keyFiles):
#                return
#            del keyFiles[-2:]
#            for keyFile in keyFiles:
#                log.info('  rm {}'.format(keyFile[1]))
#                rv = check_output(('rm', keyFile[1]))
#
#def createDKIM(keylocation, keybasename, keysize, signingConfTemplateFile, signingConfDestFile):
#    keylocation = os.path.expanduser(keylocation)
#    newKeyname = str(keybasename) + '_{:10d}'.format(int(time.time()))
#    keyTxt = check_output(('rspamadm', 'dkim_keygen', '-b', str(int(keysize)), '-s', str(newKeyname), '-k', os.path.join(keylocation, newKeyname+'.key')))
#    f = open(os.path.join(keylocation, newKeyname+'.txt'), 'w')
#    f.write(keyTxt)
#    f.close()
#    rv = check_output(('chmod', '0440', os.path.join(keylocation, newKeyname) + '.key'))
#    rv = check_output(('chown', '_rspamd:_rspamd', os.path.join(keylocation, newKeyname) + '.key'))
#    f = open(os.path.expanduser(signingConfTemplateFile), 'r')
#    templateContent = f.read()
#    f.close()
#    template = Template(templateContent)
#    confDestContent = template.render(keyname = newKeyname, keylocation = keylocation)
#    f = open(os.path.expanduser(signingConfDestFile), 'w')
#    f.write(confDestContent)
#    f.close()
#
#def findDKIMkeyTXT(keylocation, keybasename, fileending = 'txt'):
#    return findDKIMkey(keylocation, keybasename, fileending)
#
#def findDKIMkey(keylocation, keybasename, fileending = '{}'):
#    keylocation = os.path.expanduser(keylocation)
#    keyfiles = [(parse(str(keybasename)+'_{:d}.'+str(fileending), f), os.path.join(keylocation, f)) for f in os.listdir(keylocation) if os.path.isfile(os.path.join(keylocation, f))]
#    log.debug(keyfiles)
#    keyfiles = [(e[0][0], e[1]) for e in keyfiles if e[0] is not None]
#    log.debug(keyfiles)
#    return keyfiles
#
