#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from subprocess import check_output, CalledProcessError

def serviceAction(serviceName, action):
    return check_output(('sudo', 'systemctl', action, serviceName))


def reloadService(serviceName):
    return serviceAction(serviceName, 'reload')

def restartService(serviceName):
    return serviceAction(serviceName, 'restart')

def startService(serviceName):
    return serviceAction(serviceName, 'start')

def stopService(serviceName):
    return serviceAction(serviceName, 'stop')


