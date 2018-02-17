#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


from deepops import passwordFilter
import logging
import traceback
import re

logger = logging.getLogger('cryptdomainmgr')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s    [%(asctime)s]    %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

def log(msg):
    trc = traceback.extract_stack()
    return '{}/{}()/{}:    {}'.format(trc[-3][0], trc[-3][2], re.search('[^\(]*\((.*)\)', trc[-3][3]).group(1), passwordFilter(msg))

def debug(msg):
    logger.debug(log(msg))

def info(msg):
    logger.info(log(msg))

def warn(msg):
    logger.warn(log(msg))

def error(msg):
    logger.error(log(msg))

def critical(msg):
    logger.critical(log(msg))

