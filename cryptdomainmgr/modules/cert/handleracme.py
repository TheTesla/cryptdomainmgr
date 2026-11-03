#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# ACME certificate handler based on the acme library (certbot's ACME
# protocol implementation) instead of the bundled bash dehydrated.
#
# The dns-01 challenge token is published through the same mechanism as
# in the dehydrated handler: a cryptdomainmgr --update run per domain
# using the domain handler configured in the domain section (e.g.
# dnsuptools/inwx or mock for tests). Combine with the pebble ACME test
# server for fully local offline runs.

import os
import re
import time
from datetime import datetime, timedelta

import requests
import josepy
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from acme import client, messages, challenges, crypto_util, errors
from simpleloggerplus import simpleloggerplus as log
from cryptdomainmgr.cdmstatehandler import StateHandler
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir

defaultConfig = {'keysize': 4096}

ACME_RETRY_DEADLINE_SECONDS = 90


def _loadOrCreateKey(keyFilename, keysize):
    if os.path.isfile(keyFilename):
        with open(keyFilename, 'rb') as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    key = rsa.generate_private_key(public_exponent=65537, key_size=int(keysize))
    pem = key.private_bytes(serialization.Encoding.PEM,
                            serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption())
    fd = os.open(keyFilename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(pem)
    return key


def _updateDomainRecord(domainAccessTable, domain, token):
    # publish the acme challenge token in-process: call the configured
    # domain handler directly (same dispatch as domain/main.py) instead of
    # spawning a cryptdomainmgr subprocess - no credentials on the command
    # line and no shell involved
    domainConfig = dict(domainAccessTable[domain])
    handlerNames = domainConfig['handler'].split('/')
    handler = __import__('cryptdomainmgr.modules.domain.handler{}'.format(handlerNames[0]),
                         fromlist=('cryptdomainmgr', 'modules', 'domain'))
    domainConfig['acme'] = token
    handler.update(domainConfig, StateHandler(), domain)


def _splitFullchain(fullchainPem):
    blocks = re.findall(r'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',
                        fullchainPem, flags=re.DOTALL)
    return blocks[0], '\n'.join(blocks[1:])


def prepare(certConfig, certState, statedir, domainList, domainAccessTable):
    if 'acme' != certConfig['handler'].split('/')[0]:
        return
    if 0 == len(domainList):
        return

    email = certConfig['email']
    keysize = certConfig.get('keysize', 4096)
    ca = certConfig.get('ca', 'https://acme-v02.api.letsencrypt.org/directory')

    accountdir = os.path.join(statedir, 'accounts')
    makeDir(accountdir)
    accountKey = _loadOrCreateKey(os.path.join(accountdir, 'account.key'), 4096)
    certKey = _loadOrCreateKey(os.path.join(statedir, 'cert.key'), keysize)
    jwk = josepy.JWKRSA(key=accountKey)

    # requests also accepts a CA bundle path as verify_ssl value
    verifySSL = certConfig['caroot'] if 'caroot' in certConfig else True
    net = client.ClientNetwork(jwk, verify_ssl=verifySSL)
    directory = messages.Directory.from_json(net.get(ca).json())
    acmeClient = client.ClientV2(directory, net=net)
    try:
        acmeClient.new_account(messages.NewRegistration.from_data(
            email=email, terms_of_service_agreed=True))
    except errors.ConflictError as e:
        # account key already registered, reuse the existing account
        regr = messages.RegistrationResource(uri=e.location)
        net.account = regr
    log.info('Registered ACME account for {}'.format(', '.join(domainList)))

    csrPem = crypto_util.make_csr(
        certKey.private_bytes(serialization.Encoding.PEM,
                              serialization.PrivateFormat.PKCS8,
                              serialization.NoEncryption()), domainList)
    certState.setOpStateRunning()

    # DNS propagation wait before answering the challenge, with the same
    # exponential backoff strategy as the dehydrated handler (3^i seconds,
    # retry with a fresh order because an invalid authorization invalidates
    # the whole order). Configurable via the "waitsec" cert config key.
    waitsec = int(certConfig.get('waitsec', 9))
    order = None
    finalized = None
    i = 2
    while True:
        order = acmeClient.new_order(csrPem)
        # publish the dns-01 tokens before answering the challenges
        deployed = []
        try:
            for authz in order.authorizations:
                domain = authz.body.identifier.value
                for challb in authz.body.challenges:
                    if not isinstance(challb.chall, challenges.DNS01):
                        continue
                    recordName = challb.chall.validation_domain_name(domain)
                    token = challb.chall.validation(jwk)
                    log.info('Publishing dns-01 challenge for {} ({} record)'.format(domain, recordName))
                    _updateDomainRecord(domainAccessTable, domain, token)
                    deployed.append(challb)
            if 0 == len(deployed):
                raise RuntimeError('no dns-01 challenge offered for {}'.format(', '.join(domainList)))

            try:
                # first wait: waitsec (default 9 s), then x3 each retry
                wts = waitsec * (3 ** (i - 2))
                log.info('Waiting {} s for DNS propagation of the challenge records'.format(wts))
                time.sleep(wts)
                for challb in deployed:
                    acmeClient.answer_challenge(challb, challb.chall.response(jwk))
                finalized = acmeClient.poll_and_finalize(
                    order, deadline=datetime.now() + timedelta(seconds=ACME_RETRY_DEADLINE_SECONDS))
                break
            except errors.ValidationError as e:
                if 4 <= i:
                    raise
                i += 1
                log.warn('dns-01 validation failed, maybe due to DNS caching interval: {}'.format(e))
                log.warn('  -> Retrying with {} s propagation wait'.format(waitsec * (3 ** (i - 2))))
        finally:
            # clean up the challenge records of this attempt before retrying
            if order is not None:
                for authz in order.authorizations:
                    domain = authz.body.identifier.value
                    if any(isinstance(c.chall, challenges.DNS01) for c in authz.body.challenges):
                        _updateDomainRecord(domainAccessTable, domain, '')

    certdir = os.path.join(statedir, 'certs', domainList[0])
    makeDir(certdir)
    certPem, chainPem = _splitFullchain(finalized.fullchain_pem)
    timestamp = str(int(time.time()))
    # dehydrated-style layout: timestamped files with stable symlink names,
    # copyCert in cert/main.py resolves the symlinks for the rollover
    filenames = {'certfile': 'cert.pem', 'fullchainfile': 'fullchain.pem',
                 'chainfile': 'chain.pem', 'keyfile': 'privkey.pem'}
    contents = {'cert.pem': certPem, 'fullchain.pem': finalized.fullchain_pem,
                'chain.pem': chainPem,
                'privkey.pem': certKey.private_bytes(serialization.Encoding.PEM,
                                                     serialization.PrivateFormat.PKCS8,
                                                     serialization.NoEncryption())}
    for name, content in contents.items():
        stem, ext = os.path.splitext(name)
        timestampedName = '{}-{}{}'.format(stem, timestamp, ext)
        with open(os.path.join(certdir, timestampedName), 'wb' if isinstance(content, bytes) else 'w') as f:
            f.write(content)
        linkPath = os.path.join(certdir, name)
        if os.path.islink(linkPath) or os.path.exists(linkPath):
            os.remove(linkPath)
        os.symlink(timestampedName, linkPath)

    if 'running' == certState.opstate:
        certState.registerResult(dict({'domain': domainList[0],
                                       'timestamp': timestamp,
                                       'san': list(domainList)},
                                      **{k: os.path.join(certdir, v) for k, v in filenames.items()}))
    certState.setOpStateDone()
