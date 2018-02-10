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
if '--update-only' == argv[1]:
    mgr.update('prepare', argv[2:])
elif '--update' == argv[1]:
    mgr.update('', argv[2:])
    mgr.prepare()
else:
    mgr.prepare(argv[1:])

