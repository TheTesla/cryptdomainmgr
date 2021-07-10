#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from subprocess import check_output, CalledProcessError
from simpleloggerplus import simpleloggerplus as log

def serviceAction(serviceName, action):
    try:
        return check_output(('sudo', 'systemctl', action, serviceName))
    except Exception as e:
        log.error(e)
    try:
        return check_output(('systemctl', action, serviceName))
    except Exception as e:
        log.error(e)
    if 'reload' == action:
        try:
            return check_output(('killall', serviceName, '-s', 'SIGHUP'))
        except Exception as e:
            log.error(e)
    log.error("reload failed")
    raise("reload failed")

def reloadService(serviceName):
    return serviceAction(serviceName, 'reload')

def restartService(serviceName):
    return serviceAction(serviceName, 'restart')

def startService(serviceName):
    return serviceAction(serviceName, 'start')

def stopService(serviceName):
    return serviceAction(serviceName, 'stop')


