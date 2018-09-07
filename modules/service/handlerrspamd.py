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
    if i != 9:
        return
    log.info('Rspamd prepare')

def rollover(config, i=9):
    if i != 9:
        return
    log.info('Rspamd rollover (reload)')
    rv = check_output(('systemctl', 'reload', 'rspamd'))

def cleanup(config, i=0):
    if i != 9:
        return
    log.info('Rspamd cleanup')

