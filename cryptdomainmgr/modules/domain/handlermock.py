#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# Local DNS mock handler for offline tests.
#
# Implements the same interface as handlerdnsuptools but keeps all
# records in a file-backed store instead of talking to a DNS provider
# API. The record logic (TLSA/DKIM/CAA/... formatting, add/delete
# decisions and log output) is reused from dnsuptools, only the
# network layer is replaced. Combine with the pebble ACME test server
# (PEBBLE_VA_ALWAYS_VALID=1) to run the full prepare/rollover/cleanup
# flow without INWX access and without internet.

import json
import os
import tempfile

from dnsuptools import dnsuptools
from cryptdomainmgr.modules.domain import handlerdnsuptools as dnsuptoolshandler

DEFAULTSTORE = os.path.join(tempfile.gettempdir(), 'cryptdomainmgr_mockdns.json')


class MockDNSHandler:
    """File-backed DNS store mimicking the dnsuptools handler interface (info/create/update/delete)."""

    def __init__(self, storeFilename):
        self.storeFilename = storeFilename
        self.records = []
        self.nextId = 1
        self.load()

    def load(self):
        if not os.path.isfile(self.storeFilename):
            return
        with open(self.storeFilename, 'r') as f:
            state = json.load(f)
        self.records = state.get('records', [])
        self.nextId = state.get('nextId', 1)

    def save(self):
        makeDir = os.path.dirname(self.storeFilename)
        if makeDir:
            os.makedirs(makeDir, exist_ok=True)
        with open(self.storeFilename, 'w') as f:
            json.dump({'records': self.records, 'nextId': self.nextId}, f)

    def match(self, filterDict):
        recId = filterDict.get('recordId', filterDict.get('id'))
        if recId is not None:
            return [dict(e) for e in self.records if e['id'] == recId]
        rv = self.records
        for k, v in filterDict.items():
            if k in ['id', 'recordId', 'domain']:
                continue
            rv = [e for e in rv if str(e.get(k)) == str(v)]
        return [dict(e) for e in rv]

    def info(self, filterDict):
        return self.match(filterDict)

    def create(self, updateDict):
        content = updateDict.get('content')
        if content is not None:
            for e in self.records:
                if e['name'] == updateDict['name'] and e['type'] == updateDict['type'] and e['content'] == content:
                    # same behaviour as the inwx API: object already exists
                    raise ValueError('record exists', {'code': 2302})
        record = dict(updateDict)
        record['id'] = self.nextId
        self.nextId += 1
        self.records.append(record)
        self.save()
        return {'id': record['id']}

    def update(self, updateDict):
        for e in self.records:
            if e['id'] == updateDict['id']:
                e.update(updateDict)
                self.save()
                return {'id': e['id']}
        raise ValueError('no such record', {'code': 2303})

    def delete(self, deleteDict):
        ids = [e['id'] for e in self.match(deleteDict)]
        self.records = [e for e in self.records if e['id'] not in ids]
        self.save()
        return [{'id': i, 'code': 1000} for i in ids]


def getStoreFilename(domainConfig):
    return domainConfig.get('mockstore', DEFAULTSTORE)


def getAccessParams(domainConfig):
    rv = ['handler']
    if 'mockstore' in domainConfig:
        rv.append('mockstore')
    return rv


def mkDNSup(domainConfig):
    dnsup = dnsuptools.DNSUpTools()
    dnsup.setHandler(MockDNSHandler(getStoreFilename(domainConfig)))
    if 'acme' in domainConfig and domainConfig['acme']:
        # short TTL for acme challenge records, see handlerdnsuptools
        # (300 is the minimum TTL the INWX API accepts)
        dnsup.defaultTTL = 300
    return dnsup


def update(domainConfig, domainState, domainSecName):
    if 'mock' != domainConfig['handler'].split('/')[0]:
        return
    dnsup = mkDNSup(domainConfig)
    domainState.setOpStateRunning()
    dnsuptoolshandler.setACME(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setCAA(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setSOA(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setSPF(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setADSP(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setDMARCentries(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setSRV(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setIPs(domainConfig, domainState, domainSecName, dnsup)
    dnsuptoolshandler.setMX(domainConfig, domainState, domainSecName, dnsup)
    domainState.setOpStateDone()


def prepare(domainConfig, domainState, domainSecName, state):
    if 'mock' != domainConfig['handler'].split('/')[0]:
        return
    dnsup = mkDNSup(domainConfig)
    domainState.setOpStateWaiting()
    domainState.setOpStateRunning()
    tlsaReady = dnsuptoolshandler.addTLSA(domainConfig, domainState, domainSecName, dnsup, state)
    dkimReady = dnsuptoolshandler.addDKIM(domainConfig, domainState, domainSecName, dnsup, state)
    if tlsaReady and dkimReady:
        domainState.setOpStateDone()


def rollover(domainConfig, domainState, domainSecName, state):
    if 'mock' != domainConfig['handler'].split('/')[0]:
        return
    domainState.setOpStateWaiting()
    domainState.setOpStateRunning()
    domainState.setOpStateDone()


def cleanup(domainConfig, domainState, domainSecName, state):
    if 'mock' != domainConfig['handler'].split('/')[0]:
        return
    dnsup = mkDNSup(domainConfig)
    domainState.setOpStateWaiting()
    domainState.setOpStateRunning()
    tlsaReady = dnsuptoolshandler.delTLSA(domainConfig, domainState, domainSecName, dnsup, state)
    dkimReady = dnsuptoolshandler.delDKIM(domainConfig, domainState, domainSecName, dnsup, state)
    if tlsaReady and dkimReady:
        domainState.setOpStateDone()
