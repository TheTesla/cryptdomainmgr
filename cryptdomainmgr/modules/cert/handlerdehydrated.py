#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from subprocess import check_output, CalledProcessError, STDOUT
from simpleloggerplus import simpleloggerplus as log
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir
from cryptdomainmgr.modules.common.cdmprochelper import runCmd
import time

defaultConfig = {'keysize': 4096, 'extraflags': '', 'caa': {'url': 'letsencrypt.org', 'flag': '0', 'tag': 'issue'}}

def prepare(certConfig, certState, statedir, domainList, domainAccessTable):
    if 'dehydrated' != certConfig['handler'].split('/')[0]:
        return
    if 0 == len(domainList):
        return
    email = certConfig['email']
    keysize = 4096
    if 'keysize' in certConfig:
        keysize = certConfig['keysize']
    if 'extraflags' in certConfig:
        extraFlags = certConfig['extraflags']
    extraFlags = [e if '-' == e[0] else '--' + e for e in extraFlags]
    if '--staging' in extraFlags:
        ca = "https://acme-staging-v02.api.letsencrypt.org/directory"
        extraFlags.remove('--staging')
        if 'staging' in extraFlags:
            extraFlags.remove('staging')
    elif 'ca' in certConfig:
        ca = certConfig['ca']
    else:
        ca = "https://acme-v02.api.letsencrypt.org/directory"

    makeDir(os.path.realpath(statedir))
    confFilename = os.path.normpath(os.path.join(statedir, 'dehydrated.conf'))
    confFile = open(confFilename, 'w')
    confFile.write('CA={}\n'.format(str(ca)))
    confFile.write('CONTACT_EMAIL={}\n'.format(str(email)))
    confFile.write('KEYSIZE={}\n'.format(int(keysize)))
    confFile.write('CERTDIR={}\n'.format(os.path.join(statedir, 'certs')))
    confFile.write('\n')
    confFile.close()


    here = os.path.dirname(os.path.realpath(__file__))
    args = [os.path.join(here, 'dehydrated/dehydrated'), '-f', confFilename, '--accept-terms', '-c', '-t', 'dns-01', '-k', os.path.join(here, 'hook.sh')]
    log.debug(extraFlags)
    args.extend(extraFlags)
    for d in domainList:
        args.extend(['-d', str(d)])
    log.debug(args)
    certState.setOpStateRunning()

    i = 0
    while True:
        try:
            log.info('Starting DNS-01 authentication')
            rv = runCmd(' '.join(args), stderr=STDOUT, env=dict(os.environ, DOMAINACCESSTABLE=domainAccessTable, STATEDIR=statedir, WAITSEC="{}".format(3**i)))
            break
        except CalledProcessError as e:
            if 'ERROR: Lock file' in e.output:
                lockFilename = e.output.decode().split('ERROR: Lock file \'')[-1].split('\' present, aborting')[0]
                log.warn('Lock file from imcomplete run found: {}'.format(lockFilename))
                log.warn('  -> Removing')
                os.remove(lockFilename)
            elif 'Incorrect TXT record' in e.output:
                log.info('  -> Invalid DNS-01 challenge, maybe due to DNS caching interval. Trying to wait longer!')
                i += 1
                log.info('  -> Will wait {} s to give challenge time to propagate DNS cache.'.format(3**i))
            elif 'NXDOMAIN' in e.output:
                log.info('  -> Missing DNS-01 challenge, maybe due to DNS caching interval. Trying to wait longer!')
                i += 1
                log.info('  -> Will wait {} s to give challenge time to propagate DNS cache.'.format(3**i))
            else:
                raise(e)
            if 9 == i:
                raise(e)

    res = []
    rv = rv.splitlines()
    for s, e in enumerate(rv):
        if '---- DEPLOYMENTRESULT ----' == e[:len('---- DEPLOYMENTRESULT ----')]:
            break
    for i, e in enumerate(rv[s+1:]):
        if '---- END DEPLOYMENTRESULT ----' == e[:len('---- END DEPLOYMENTRESULT ----')]:
            break
        res.append(e)
    resDict = {e.split('=')[0].lower(): e.split('=')[1] for e in res}
    resDict['san'] = list(domainList)

    if 'running' == certState.opstate:
        certState.registerResult(resDict)
    certState.setOpStateDone()

    return rv


