#!/usr/bin/env python
# -*- encoding: UTF8 -*-

from cryptdomainmgr import *
from sys import argv

mgr = ManagedDomain()
mgr.cleanup(argv[1])

