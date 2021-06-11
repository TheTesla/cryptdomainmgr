#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
import subprocess as sp
import os
from test.test_config import testdh, dhfile
from cryptdomainmgr.modules.common.cdmprochelper import runCmd



class TestHandlerOpenssl(unittest.TestCase):
    def testHandlerOpensslDH512(self):
        try:
            os.remove(dhfile)
        except:
            pass
        stdout = runCmd("python3 -m cryptdomainmgr --prepare \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [dhparam] \
        handler=openssl \
        [dhparam:{}] \
        keysize=512 \
        filename={} \
        ' 2>&1".format(testdh,dhfile))

        with self.subTest("check dhparam log output"):
            self.assertRegex(stdout, ".*Create dhparams.*{}.*".format(testdh))
        with self.subTest("check dhparam file exists"):
            self.assertFalse(os.path.isfile(dhfile))

        stdout = runCmd("python3 -m cryptdomainmgr --rollover \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir=/tmp/test_cryptdomainmgr \
        [dhparam] \
        handler=openssl \
        [dhparam:{}] \
        keysize=512 \
        filename={} \
        ' 2>&1".format(testdh,dhfile))

        with self.subTest("check dhparam log output"):
            self.assertRegex(stdout, ".*Apply dhparams.*{}.*".format(testdh))
        with self.subTest("check dhparam file exists"):
            self.assertTrue(os.path.isfile(dhfile))


