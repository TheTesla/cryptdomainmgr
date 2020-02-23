#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from subprocess import check_output, CalledProcessError
from simpleloggerplus import simpleloggerplus as log
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir
import time

defaultConfig = {'filename': '/etc/myssl/dh2048.pem', 'keysize': 2048}

def prepare(dhparamConfig, dhparamState, statedir, dhparamSecName): 
    if 'openssl' != dhparamConfig['handler'].split('/')[0]:
        return
    keysize = 2048
    if 'keysize' in dhparamConfig:
        keysize = dhparamConfig['keysize']

    path = os.path.realpath(os.path.join(statedir, 'dhparams', dhparamSecName))
    makeDir(os.path.dirname(path))

    dhparamState.setOpStateRunning()
    try:
        rv = check_output(('openssl', 'dhparam', '-out', str(path), str(int(keysize))))
        log.info(rv)
    except CalledProcessError as e:
        log.error(e.output)
        time.sleep(1)
        raise(e)

    resDict = {}
    resDict['tmpfile'] = path
    
    if 'running' == dhparamState.opstate:
        dhparamState.registerResult(resDict)
    dhparamState.setOpStateDone()

    return rv


