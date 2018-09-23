#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from dnsuptools import dnsuptools 
from simpleloggerplus import simpleloggerplus as log
from OpenSSL import crypto

def update(domainConfig, domainState, domainSecName):
    handlers = domainConfig['handler'].split('/')
    if 'dnsuptools' != handlers[0]:
        return
    dnsup = dnsuptools.DNSUpTools()
    dnsup.setHandler(handlers[1])
    dnsup.handler.setUserDict({'default': domainConfig['user'], domainSecName: domainConfig['user']})
    dnsup.handler.setPasswdDict({'default': domainConfig['passwd'], domainSecName: domainConfig['passwd']})
    
    domainState.setOpStateRunning()
    
    setACME(domainConfig, domainState, domainSecName, dnsup)
    setCAA(domainConfig, domainState, domainSecName, dnsup)
    setSOA(domainConfig, domainState, domainSecName, dnsup)
    setSPF(domainConfig, domainState, domainSecName, dnsup)
    setADSP(domainConfig, domainState, domainSecName, dnsup)
    setDMARCentries(domainConfig, domainState, domainSecName, dnsup)
    setSRV(domainConfig, domainState, domainSecName, dnsup)
    setIPs(domainConfig, domainState, domainSecName, dnsup)
    setMX(domainConfig, domainState, domainSecName, dnsup)

    domainState.setOpStateDone()

    return

def prepare(domainConfig, domainState, domainSecName, state): 
    handlers = domainConfig['handler'].split('/')
    if 'dnsuptools' != handlers[0]:
        return
    dnsup = dnsuptools.DNSUpTools()
    dnsup.setHandler(handlers[1])
    print({domainSecName: domainConfig['user']})
    dnsup.handler.setUserDict({'default': domainConfig['user'], domainSecName: domainConfig['user']})
    dnsup.handler.setPasswdDict({'default': domainConfig['passwd'], domainSecName: domainConfig['passwd']})
    
    
    domainState.setOpStateWaiting()
    
    domainState.setOpStateRunning()
    addTLSA(domainConfig, domainState, domainSecName, dnsup, state)
    addDKIM(domainConfig, domainState, domainSecName, dnsup, state)

    domainState.setOpStateDone()

    return

def rollover(domainConfig, domainState, domainSecName, state): 
    handlers = domainConfig['handler'].split('/')
    if 'dnsuptools' != handlers[0]:
        return
    
    domainState.setOpStateWaiting()
    
    domainState.setOpStateRunning()

    domainState.setOpStateDone()

    return

def cleanup(domainConfig, domainState, domainSecName, state): 
    handlers = domainConfig['handler'].split('/')
    if 'dnsuptools' != handlers[0]:
        return
    dnsup = dnsuptools.DNSUpTools()
    dnsup.setHandler(handlers[1])
    print({domainSecName: domainConfig['user']})
    dnsup.handler.setUserDict({'default': domainConfig['user'], domainSecName: domainConfig['user']})
    dnsup.handler.setPasswdDict({'default': domainConfig['passwd'], domainSecName: domainConfig['passwd']})
    
    domainState.setOpStateWaiting()
    
    domainState.setOpStateRunning()
    setTLSA(domainConfig, domainState, domainSecName, dnsup, state)
    setDKIM(domainConfig, domainState, domainSecName, dnsup, state)

    domainState.setOpStateDone()

    return

def getCertSAN(filename):
    certFile = open(filename, 'rt').read()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certFile)
    san = [cert.get_extension(i).get_data().split('\x82')[1:] for i in range(cert.get_extension_count()) if 'subjectAltName' == cert.get_extension(i).get_short_name()][0]
    san = [e[1:] for e in san]
    return san

def getFullchain(state, domainContent):
    certState = state.getSubstate('cert').getSubstate(domainContent['certificate'])
    return certState.result['fullchainfile']

def isCertReady(state, domainContent):
    certState = state.getSubstate('cert').getSubstate(domainContent['certificate'])
    return certState.isDone()

def isDKIMready(state, domainContent):
    certState = state.getSubstate('dkim').getSubstate(domainContent['dkim'])
    return certState.isDone()

def setSPF(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('setspf')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'spfAggrDel' in domainConfig and 'spfAggrAdd' in domainConfig:
        dnsup.setSPFentry(domainSecName, domainConfig['spfAggrAdd'], domainConfig['spfAggrDel'])
    elif 'spfAggrDel' in domainConfig:
        dnsup.setSPFentry(domainSecName, {}, domainConfig['spfAggrDel'])
    elif 'spfAggrAdd' in domainConfig:
        dnsup.setSPFentry(domainSecName, domainConfig['spfAggrAdd'], {})
    rrState.setOpStateDone()

def setDMARCentries(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('setdmarcentries')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'dmarc' in domainConfig:
        # following line means configuration:
        # dmarc = 
        # this deletes all entries not specified
        # if no configuration like:
        # dmarc = 
        # is specified, so only given dmarc subparameters are overwritten
        # all this is managed by dnsuptools:
        dnsup.setDMARCentry(domainSecName, domainConfig['dmarc'])
    rrState.setOpStateDone()

def setADSP(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('setadsp')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'adsp' in domainConfig:
        dnsup.setADSP(domainSecName, domainConfig['adsp'])
    rrState.setOpStateDone()

def setACME(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('setacme')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'acme' in domainConfig:
        dnsup.setACME(domainSecName, domainConfig['acme'])
    rrState.setOpStateDone()

def setSOA(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('setsoa')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'soa' in domainConfig:
        dnsup.setSOAentry(domainSecName, domainConfig['soa'])
    rrState.setOpStateDone()

def addSRV(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('addsrv')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'srvAggrAdd' in domainConfig:
        dnsup.addSRV(domainSecName, domainConfig['srvAggrAdd']) 
    rrState.setOpStateDone()

def delSRV(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('delsrv')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'srvAggrDel' in domainConfig:
        dnsup.delSRV(domainSecName, domainConfig['srvAggrDel'], domainConfig['srvAggrAdd']) 
    rrState.setOpStateDone()

def setSRV(domainConfig, domainState, domainSecName, dnsup):
    addSRV(domainConfig, domainState, domainSecName, dnsup)
    delSRV(domainConfig, domainState, domainSecName, dnsup)

def addCAA(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('addcaa')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'caaAggrAdd' in domainConfig:
        dnsup.addCAA(domainSecName, domainConfig['caaAggrAdd'])
    rrState.setOpStateDone()

def delCAA(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('delcaa')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'caaAggrDel' in domainConfig:
        dnsup.delCAA(domainSecName, domainConfig['caaAggrDel'], domainConfig['caaAggrAdd'])
    rrState.setOpStateDone()

def setCAA(domainConfig, domainState, domainSecName, dnsup):
    addCAA(domainConfig, domainState, domainSecName, dnsup)
    delCAA(domainConfig, domainState, domainSecName, dnsup)

def delIPs(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('delips')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'ip4AggrDel' in domainConfig:
        dnsup.delA(domainSecName, [e['content'] if 'content' in e else '*' for e in domainConfig['ip4AggrDel']], [e['content']  for e in domainConfig['ip4AggrAdd']]) 
    if 'ip6AggrDel' in domainConfig:
        dnsup.delAAAA(domainSecName, [e['content'] if 'content' in e else '*' for e in domainConfig['ip6AggrDel']], [e['content']  for e in domainConfig['ip6AggrAdd']]) 
    rrState.setOpStateDone()

def addIPs(domainConfig, domainState, domainSecName, dnsup): 
    rrState = domainState.getSubstate('addips')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'ip4AggrAdd' in domainConfig:
        dnsup.addA(domainSecName, [e['content']  for e in domainConfig['ip4AggrAdd']]) 
    if 'ip6AggrAdd' in domainConfig:
        dnsup.addAAAA(domainSecName, [e['content']  for e in domainConfig['ip6AggrAdd']]) 
    rrState.setOpStateDone()
    return

def setIPs(domainConfig, domainState, domainSecName, dnsup): 
    addIPs(domainConfig, domainState, domainSecName, dnsup)
    delIPs(domainConfig, domainState, domainSecName, dnsup)

def addMX(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('addmx')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'mxAggrAdd' in domainConfig:
        dnsup.addMX(domainSecName, domainConfig['mxAggrAdd'])
    rrState.setOpStateDone()
        
def delMX(domainConfig, domainState, domainSecName, dnsup):
    rrState = domainState.getSubstate('delmx')
    if rrState.isDone():
        return 
    rrState.setOpStateRunning()
    if 'mxAggrDel' in domainConfig:
        dnsup.delMX(domainSecName, domainConfig['mxAggrDel'], domainConfig['mxAggrAdd'])
    rrState.setOpStateDone()

def setMX(domainConfig, domainState, domainSecName, dnsup):
    addMX(domainConfig, domainState, domainSecName, dnsup)
    delMX(domainConfig, domainState, domainSecName, dnsup)



def addTLSA(domainConfig, domainState, domainSecName, dnsup, state):
    setTLSA(domainConfig, domainState, domainSecName, dnsup, state, addOnly = True)

def setTLSA(domainConfig, domainState, domainSecName, dnsup, state, addOnly=False):
    rrState = domainState.getSubstate('settlsa')
    if rrState.isDone():
        return
    if 'tlsa' in domainConfig:
        rrState.setOpStateWaiting()
        if not isCertReady(state, domainConfig):
            return
        rrState.setOpStateRunning()
        cert = getFullchain(state, domainConfig)
        print(cert)
        if cert is None:
            log.info('not deploying TLSA record for {} (no certificate)'.format(domainSecName))
        else:
            log.info('deploying TLSA record for {} (certificate found)'.format(domainSecName))
            sanList = getCertSAN(cert)
            log.info('  -> found certificate: {} for: {}'.format(cert, ', '.join(sanList)))
            if domainSecName not in sanList:
                log.error('{} not in certificate {}'.format(domainSecName, cert))
            if addOnly is True:
                dnsup.addTLSAfromCert(domainSecName, cert, domainConfig['tlsa'])
            else:
                dnsup.setTLSAfromCert(domainSecName, cert, domainConfig['tlsa'])
    rrState.setOpStateDone()



def addDKIM(domainConfig, domainState, domainSecName, dnsup, state, delete = False):
    rrState = domainState.getSubstate('adddkim')
    if rrState.isDone():
        return 
    if 'dkim' in domainConfig:
        rrState.setOpStateWaiting()
        if not isDKIMready(state, domainConfig):
            return
        rrState.setOpStateRunning()
        keys = findDKIMkeyTXT(dkimContent['keylocation'], dkimContent['keybasedomainSecName'])
        keys = [f[1] for f in keys]
        domainsOfSameDKIM = {k:v for k, v in domainConfig.items() if 'dkim' in v and dkimSecName == v['dkim']}
        log.debug(keys)
        for domainSecName, domainConfig in domainsOfSameDKIM.items():
            log.debug((domainSecName, keys))
            if delete is True:
                dnsup.setDKIMfromFile(domainSecName, keys)
            else:
                dnsup.addDKIMfromFile(domainSecName, keys)
    rrState.setOpStateDone()


def setDKIM(domainConfig, domainState, domainSecName, dnsup, state):
    addDKIM(domainConfig, domainState, domainSecName, dnsup, state, True)




