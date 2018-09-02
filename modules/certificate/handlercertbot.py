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

def createCert(domainList, conf): 
    if 'certbot' != conf['handler']:
        return
    if 0 == len(domainList):
        return
    email = conf['email']
    keysize = 4096
    if 'keysize' in conf:
        keysize = conf['keysize']
    if 'extraflags' in conf:
        extraFlags = conf['extraflags']
    extraFlags = [e if '-' == e[0] else '--' + e for e in extraFlags]
    args = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'certbot/certbot-auto'), 'certonly', '--email', str(email), '--agree-tos', '--non-interactive', '--standalone', '--expand', '--rsa-key-size', str(int(keysize))]
    log.debug(extraFlags)
    args.extend(extraFlags)
    for d in domainList:
        args.extend(['-d', str(d)])
    log.debug(args)
    rv = check_output(args)
    return rv

