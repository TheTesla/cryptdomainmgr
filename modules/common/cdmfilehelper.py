#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os

def makeDir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise   
        pass

