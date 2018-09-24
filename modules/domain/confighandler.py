#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from simpleloggerplus import simpleloggerplus as log

def filterEntries(content, rrType):
    return {k: v for k, v in content.items() if rrType == k[:len(rrType)]}

def splitList(content):
    return {k: [e.strip() for e in v.split(',')] for k, v in content.items()}

def parseNestedEntry(key, value, default = [], keySplitPattern = '.', valueSplitPattern = ':'):
    if keySplitPattern is None:
        keyList = [key]
    else:
        keyList   = key.split(keySplitPattern)
    if valueSplitPattern is None:
        valueList = [value]
    else:
        valueList = value.split(valueSplitPattern)
    addList   = list(default)
    rv = {}
    subtractMode = False
    if '+' == keyList[-1][-1]:
        keyList[-1] = keyList[-1][:-1]
    elif '-' == keyList[-1][-1]:
        keyList[-1] = keyList[-1][:-1]
        subtractMode = True
    else:
        rv['delList'] = list(keyList)
    addList[:len(keyList)] = list(keyList)
    for i, e in enumerate(valueList):
        addList[-i] = e
    if subtractMode is True:
        rv['delListWithContent'] = addList
    else:
        rv['addList'] = addList
    return rv 

def list2dict(entry, hasContent, keys):
    entry.extend(['*'] * (len(keys) - len(entry)))
    rv = {key: entry[i] for i, key in enumerate(keys)}
    rv = {k: v for k, v in rv.items() if '*' != v}
    if hasContent is False:
        if keys[0] in rv:
            del rv[keys[0]]
    return rv

def list2set(entry, hasContent):
    if hasContent is False:
        return set(entry[1:])
    return set(entry)

def list2SPF(spfEntry, hasContent = True):
    if hasContent is False:
        return '*'
    return spfEntry[0]

def list2CAA(caaEntry, hasContent = True):
    return list2dict(caaEntry, hasContent, ['flag', 'url', 'tag'])

def list2SRV(srvEntry, hasContent = True):
    return list2dict(srvEntry, hasContent, ['server', 'service', 'proto', 'port', 'weight', 'prio'])

def list2MX(mxEntry, hasContent = True):
    return list2dict(mxEntry, hasContent, ['content', 'prio'])

def list2ip(ipEntry, hasContent = True):
    return list2dict(ipEntry, hasContent, ['content'])

def list2rrType(rrType, entry, hasContent = True):
    if 'mx' == rrType:
        return list2MX(entry, hasContent)
    elif 'srv' == rrType:
        return list2SRV(entry, hasContent)
    elif 'ip4' == rrType:
        return list2ip(entry, hasContent)
    elif 'ip6' == rrType:
        return list2ip(entry, hasContent)
    elif 'caa' == rrType:
        return list2CAA(entry, hasContent)
    elif 'spf' == rrType:
        return list2SPF(entry, hasContent)
    log.error('rrType not supported')
    assert TypeError('rrType not supported')

def interpreteRR(content, rrType = 'mx', defaultList = ['*', '10'], keySplitPattern = '.', valueSplitPattern = ':'):
    x = filterEntries(content, rrType)
    conf = splitList(x)
    parsedList = [parseNestedEntry(k, e, defaultList, keySplitPattern, valueSplitPattern) for k, v in conf.items() for e in v]
    aggrAdd = [list2rrType(rrType, e['addList']) for e in parsedList if 'addList' in e]
    aggrDel = [list2rrType(rrType, e['delList'], False) for e in parsedList if 'delList' in e]
    aggrDelWithContent = [list2rrType(rrType, e['delListWithContent']) for e in parsedList if 'delListWithContent' in e]
    aggrDel.extend(aggrDelWithContent)
    return {'{}AggrAdd'.format(rrType): aggrAdd, '{}AggrDel'.format(rrType): aggrDel}

def interpreteCAA(content):
    return interpreteRR(content, 'caa', ['*', '*', '*'], '.', ' ')

def interpreteMX(content):
    return interpreteRR(content, 'mx', ['*', '10'])

def interpreteSRV(content):
    return interpreteRR(content, 'srv', ['*', '*', '*', '*', '50', '10'])

def interpreteA(content):
    return interpreteRR(content, 'ip4', ['*'])

def interpreteAAAA(content):
    return interpreteRR(content, 'ip6', ['*'], None, None)

def interpreteDictRR(content, rrType):
    if rrType in [k.split('.')[0] for k in content.keys()]:
        rrDict = {k.split('.')[1] if 1 < len(k.split('.')) else '' : v  for k, v in content.items() if rrType == k.split('.')[0]}
        return {rrType: rrDict}
    return {}

def interpreteSetRR(content, rrType, defaultList = ['*']):
    rrList = interpreteRR(content, rrType, defaultList)
    rrSet = {k: set([e for e in v if '' != e]) for k, v in rrList.items()}
    return rrSet

def interpreteDMARC(content):
    return interpreteDictRR(content, 'dmarc')

def interpreteSOA(content):
    return interpreteDictRR(content, 'soa')

def interpreteSPF(content):
    return interpreteSetRR(content, 'spf', ['*'])

def interpreteConfig(cr, sh):
    domainconfig = cr.getRawConfigOf('domain', True)
    domainconfig = applyDefault(domainconfig) # must be here because following section depends on default values

    for domain, content in domainconfig.items():
        ip4 = interpreteA(content)
        domainconfig[domain].update(ip4)
        ip6 = interpreteAAAA(content)
        domainconfig[domain].update(ip6)
        mx = interpreteMX(content)
        domainconfig[domain].update(mx)
        srv = interpreteSRV(content)
        domainconfig[domain].update(srv)
        caa = interpreteCAA(content)
        domainconfig[domain].update(caa)
        dmarc = interpreteDMARC(content)
        domainconfig[domain].update(dmarc)
        soa = interpreteSOA(content)
        domainconfig[domain].update(soa)
        spf = interpreteSPF(content)
        domainconfig[domain].update(spf)

        if 'tlsa' in content:
            tlsa = str(domainconfig[domain]['tlsa'])
            if 'auto' == tlsa:
                tlsa = [[3, 0, 1], [3, 0, 2], [3, 1, 1], [3, 1, 2], [2, 0, 1], [2, 0, 2], [2, 1, 1], [2, 1, 2]]
            else:
                tlsa = [[int(f) for f in e] for e in tlsa.replace(' ', '').split(',')]
            domainconfig[domain]['tlsa'] = tlsa

    log.debug(domainconfig)
    cr.updateConfig({'domain': domainconfig})
    return domainconfig

def applyDefault(config, defaultConfig={}):
    default = dict(defaultConfig)
    if 'DEFAULT' in config:
        default.update(config['DEFAULT'])
    newconfig = {}
    for section, content in config.items():
        newconfig[section] = dict(default)
        newconfig[section].update(content)
    return newconfig




