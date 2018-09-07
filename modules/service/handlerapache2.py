#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from simpleloggerplus import simpleloggerplus as log
from subprocess import check_output

def prepare(config, i=0):
    if i == 1:
        log.info('Apache2 prepare (stop)')
        rv = check_output(('systemctl', 'stop', 'apache2'))
    elif i == 9:
        log.info('Apache2 prepare (start)')
        rv = check_output(('systemctl', 'start', 'apache2'))

def rollover(config, i=9):
    if i != 9:
        return
    log.info('Apache2 rollover (restart)')
    rv = check_output(('systemctl', 'restart', 'apache2'))

def cleanup(config, i=0):
    if i != 9:
        return
    log.info('Apache2 cleanup')

