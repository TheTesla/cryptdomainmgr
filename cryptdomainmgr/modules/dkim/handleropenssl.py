#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# DKIM key handler based on the cryptography library: generates the DKIM
# key pair locally without rspamd and without sudo. Use this handler when
# the signing mail server only needs the key files (the rspamd signing
# setup with keylocation/keyname and the signing config file still works,
# only the key generation itself is decoupled from rspamd). The DNS TXT
# record publication of the public key works the same as with the rspamd
# handler (domain handler dkim=auto).

import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from simpleloggerplus import simpleloggerplus as log
from jinja2 import Template
import time
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir

here = os.path.dirname(os.path.realpath(__file__))
defaultConfig = {'keysize': 2048, 'keybasename': 'key', 'keylocation': '/var/lib/rspamd/dkim', 'keyname': 'dkim.key', 'signingconfdestinationfile': '/etc/rspamd/local.d/dkim_signing.conf', 'signingconftemplatefile': os.path.join(here, 'dkim_signing_template.conf')}


def prepare(dkimConfig, dkimState, statedir):
    if 'openssl' != dkimConfig['handler'].split('/')[0]:
        return
    res = createDKIM(dkimConfig['keysize'], os.path.join(statedir, 'key', 'dkim.key'))
    keySelector = createSelector(dkimConfig['keybasename'])
    u = createConf(dkimConfig['signingconftemplatefile'], os.path.join(statedir, 'conf', 'dkim.conf'), os.path.join(dkimConfig['keylocation'], dkimConfig['keyname']), keySelector)
    res.update(u)
    dkimState.registerResult(res)
    dkimState.setOpStateDone()

def rollover(dkimConfig, dkimState):
    if 'openssl' != dkimConfig['handler'].split('/')[0]:
        return
    log.info('using new dkim key, moving new config file')
    copyDKIM(dkimConfig, dkimState)
    copyConf(dkimConfig, dkimState)
    dkimState.setOpStateDone()

def cleanup(dkimConfig, dkimState):
    if 'openssl' != dkimConfig['handler'].split('/')[0]:
        return
    dkimState.setOpStateDone()

def copyDKIM(dkimConfig, dkimState):
    src = dkimState.result['keyfile']
    dest = os.path.join(dkimConfig['keylocation'], dkimConfig['keyname'])
    log.info('  {} -> {}'.format(src, dest))
    makeDir(str(os.path.dirname(dest)))
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'wb') as srcFile, open(src, 'rb') as keyFile:
        srcFile.write(keyFile.read())

def copyConf(dkimConfig, dkimState):
    src = dkimState.result['signingconftemporaryfile']
    dest = dkimConfig['signingconfdestinationfile']
    log.info('  {} -> {}'.format(src, dest))
    makeDir(str(os.path.dirname(dest)))
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as destFile, open(src, 'r') as confFile:
        destFile.write(confFile.read())

def createSelector(keybasename):
    return str(keybasename) + '_{:10d}'.format(int(time.time()))

def createDKIM(keysize, destination):
    """Generate a DKIM RSA key pair with cryptography and return the DNS
    TXT record fields (v, k, p) the same way the rspamadm dkim_keygen
    output is parsed in handlerrspamd."""
    makeDir(os.path.dirname(str(destination)))
    key = rsa.generate_private_key(public_exponent=65537, key_size=int(keysize))
    pem = key.private_bytes(serialization.Encoding.PEM,
                            serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption())
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(pem)
    pubkey = key.public_key().public_bytes(serialization.Encoding.DER,
                                           serialization.PublicFormat.SubjectPublicKeyInfo)
    import base64
    p = base64.b64encode(pubkey).decode()
    return {'v': 'DKIM1', 'k': 'rsa', 'p': p, 'keyfile': str(destination)}


def createConf(signingConfTemplateFile, signingConfDestFile, keyFile, keySelector):
    f = open(os.path.expanduser(signingConfTemplateFile), 'r')
    templateContent = f.read()
    f.close()
    template = Template(templateContent)
    confDestContent = str(template.render(keyselector=keySelector, keyfile=keyFile))
    makeDir(str(os.path.dirname(signingConfDestFile)))
    f = open(os.path.expanduser(signingConfDestFile), 'w')
    f.write(confDestContent)
    f.close()
    return {'signingconftemporaryfile': signingConfDestFile, 'keyname': keySelector}
