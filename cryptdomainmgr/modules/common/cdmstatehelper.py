#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


# returns also True if section/module not in config
#def isReady(serviceConfig, state, sec):
#    print(type(sec))
#    print(sec)
#    if type(sec) is list:
#        for e in sec:
#            if isReady(serviceConfig, state, e) is False:
#                return False
#        return True
#    subState = state.getSubstate(sec)
#    if sec not in serviceConfig:
#        return True
#    print(serviceConfig)
#    if type(serviceConfig[sec]) is not list:
#        print(type(serviceConfig[sec]))
#        raise Exception
#    return 0 == len([0 for e in serviceConfig[sec] if not subState.getSubstate(e).isDone()])

def isReady(secConf, state, depSec):
    if 'requires' not in secConf:
        return True
    requires = secConf['requires']
    if type(depSec) is list:
        for e in depSec:
            if isReady(secConf, state, e) is False:
                return False
        return True
    subState = state.getSubstate(depSec)
    if depSec not in requires:
        return True
    return 0 == len([0 for e in requires[depSec] if not subState.getSubstate(e).isDone()])



