#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import handlerapache2
import handlerrspamd
import handlerdovecot
import handlerpostfix

def prepare(config, i=0):
    handlerapache2.prepare(config, i)
    handlerrspamd.prepare(config, i)
    handlerpostfix.prepare(config, i)
    handlerdovecot.prepare(config, i)

def rollover(config, i=9):
    handlerapache2.rollover(config, i)
    handlerrspamd.rollover(config, i)
    handlerpostfix.rollover(config, i)
    handlerdovecot.rollover(config, i)

def cleanup(config, i=0):
    handlerapache2.cleanup(config, i)
    handlerrspamd.cleanup(config, i)
    handlerpostfix.cleanup(config, i)
    handlerdovecot.cleanup(config, i)

