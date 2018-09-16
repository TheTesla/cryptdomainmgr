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

defaultCertConfig = {'source': '/etc/letsencrypt/live', 'certname': 'fullchain.pem', 'keysize': 4096, 'extraflags': ''}

def prepare(certConfig, certState, domainList, i=2): 
    if 'certbot' != certConfig['handler']:
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
    args = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certbot/certbot-auto'), 'certonly', '--email', str(email), '--agree-tos', '--non-interactive', '--standalone', '--expand', '--rsa-key-size', str(int(keysize))]
    log.debug(extraFlags)
    args.extend(extraFlags)
    for d in domainList:
        args.extend(['-d', str(d)])
    log.debug(args)
    rv = check_output(args)
    return rv

