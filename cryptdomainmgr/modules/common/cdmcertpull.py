#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

"""Certificate pull for service handlers.

Service handlers (apache2, dovecot, postfix, ...) can pull the staged
certificates of the cert sections they reference into their own
destination directory at rollover, instead of relying on the central
cert deployment (cert section destination). Enable with:

    [service:apache2]
    handler=apache2
    cert=mailcert            # cert section(s) to pull (also drives isReady)
    certdestination=/etc/apache2/ssl
"""

import os
import shutil
from simpleloggerplus import simpleloggerplus as log
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir

CERTRESULTFILES = ['fullchainfile', 'chainfile', 'certfile', 'keyfile']


def pullCerts(serviceConfig, state):
    """Copy the staged cert files of the referenced cert sections into
    certdestination/<san>/ (same layout as the cert module deployment).

    No-op when certdestination is unset/empty. Returns the list of
    destination directories written."""
    destRoot = serviceConfig.get('certdestination', '')
    if 0 == len(str(destRoot)):
        return []
    certNames = [c for c in serviceConfig.get('cert', []) if 'auto' != c and 'DEFAULT' != c]
    if 0 == len(certNames):
        log.warn('certdestination set but no cert section referenced (cert=...), no certificates pulled')
        return []
    copied = []
    for certName in certNames:
        result = state.getSubstate('cert').getSubstate(certName).result
        if 0 == len(result):
            log.warn('cert section "{}" has no result, skipping cert pull'.format(certName))
            continue
        for name in result['san']:
            dest = os.path.join(str(destRoot), name)
            makeDir(str(dest))
            for k in CERTRESULTFILES:
                src = os.path.join(os.path.dirname(result[k]), os.readlink(result[k]))
                shutil.copy2(src, os.path.join(dest, os.path.basename(result[k])))
                log.info('  {} -> {}'.format(src, os.path.join(dest, os.path.basename(result[k]))))
            copied.append(dest)
    return copied
