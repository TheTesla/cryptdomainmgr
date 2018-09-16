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

defaultCertConfig = {'source': '/etc/dehydrated/certs', 'certname': 'fullchain.pem', 'keysize': 4096, 'extraflags': ''}

def prepare(certConfig, domainList, i=2): 
    if 'dehydrated' != certConfig['handler']:
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
        ca = "https://acme-staging.api.letsencrypt.org/directory"
        extraFlags.remove('--staging')
        if 'staging' in extraFlags:
            extraFlags.remove('staging')
    elif 'ca' in certConfig:
        ca = certConfig['ca']
    else:
        ca = "https://acme-v02.api.letsencrypt.org/directory"

    if not os.path.isdir(os.path.join(certConfig['source'], '..')):
        os.makedirs(os.path.join(certConfig['source'], '..'))

    confFilename = os.path.join(certConfig['source'],'../dehydrated.conf')
    confFile = open(confFilename, 'w')
    confFile.write('CA={}\n'.format(str(ca)))
    confFile.write('CONTACT_EMAIL={}\n'.format(str(email)))
    confFile.write('KEYSIZE={}\n'.format(int(keysize)))
    confFile.write('\n')
    confFile.close()


    here = os.path.dirname(os.path.realpath(__file__))
    args = [os.path.join(here, 'dehydrated/dehydrated'), '-f', confFilename, '--accept-terms', '-c', '-t', 'dns-01', '-k', os.path.join(here, 'hook.sh')]
    log.debug(extraFlags)
    args.extend(extraFlags)
    for d in domainList:
        args.extend(['-d', str(d)])
    log.debug(args)
    rv = check_output(args)

    print(rv)
    res = []
    rv = rv.splitlines()
    for s, e in enumerate(rv):
        print('t')
        print(e)
        if '---- DEPLOYMENTRESULT ----' == e[:len('---- DEPLOYMENTRESULT ----')]:
            break
    for i, e in enumerate(rv[s+1:]):
        print('e')
        print(e)
        if '---- END DEPLOYMENTRESULT ----' == e[:len('---- END DEPLOYMENTRESULT ----')]:
            break
        res.append(e)
    print(res)
    resDict = {e.split('=')[0]: e.split('=')[1] for e in res}
    print(resDict)

    return rv


