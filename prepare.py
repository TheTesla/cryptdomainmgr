#!/usr/bin/env python
# -*- encoding: UTF8 -*-

from cryptdomainmgr import *
from sys import argv

mgr = ManagedDomain()
mgr.prepare(argv[1])

