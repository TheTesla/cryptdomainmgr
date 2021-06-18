#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


# returns also True if section/module not in config
def isReady(serviceConfig, state, sec):
    if type(sec) is list:
        for e in sec:
            if isReady(serviceConfig, state, e) is False:
                return False
        return True
    subState = state.getSubstate(sec)
    if sec not in serviceConfig:
        return True
    return 0 == len([0 for e in serviceConfig[sec] if not subState.getSubstate(e).isDone()])

