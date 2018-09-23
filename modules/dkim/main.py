#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from subprocess import check_output
from simpleloggerplus import simpleloggerplus as log
from jinja2 import Template
from parse import parse
import handlerrspamd

def prepare(config, state):
    subState = state.getSubstate('dkim')
    for dkimSecName, dkimConfig in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        log.info("Preparing DKIM key for dkim-section: \"{}\"".format(dkimSecName))
        if 'handler' not in dkimConfig:
            continue
        dkimState = subState.getSubstate(dkimSecName)
        handlerrspamd.prepare(dkimConfig, dkimState, i)

def rollover(config, state):
    subState = state.getSubstate('dkim')
    for dkimSecName, dkimConfig in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        if 'handler' not in dkimConfig:
            continue
        dkimState = subState.getSubstate(dkimSecName)
        handlerrspamd.rollover(dkimConfig, dkimState)

def cleanup(config, state):
    subState = state.getSubstate('dkim')
    for dkimSecName, dkimConfig in config['dkim'].items():
        if 'DEFAULT' == dkimSecName:
            continue
        if 'handler' not in dkimConfig:
            continue
        dkimState = subState.getSubstate(dkimSecName)
        handlerrspamd.cleanup(dkimConfig, dkimState)

