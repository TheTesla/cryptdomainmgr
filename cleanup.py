#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

from cryptdomainmgr import *
from sys import argv

mgr = ManagedDomain()
mgr.cleanup(argv[1:])

