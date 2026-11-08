#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# Offline test for the rspamd service handler: renders the rspamd dkim
# signing config from the dkim section result (openssl key handler, mock
# domain handler). rspamd itself is not needed - the reload step is
# disabled via config, the rendered config file is asserted on disk.

import unittest
import os
import re
import shutil
from test.test_config import testdomain
from cryptdomainmgr.modules.common.cdmprochelper import runCmd

tmpdirRspamdConf = "/tmp/test_cryptdomainmgr_rspamdconf"


class TestServiceHandlerRspamdConf(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(tmpdirRspamdConf, ignore_errors=True)

    def testRspamdSigningConfRendered(self):
        conf = '\n'.join([
            "[cdm]", "statedir=" + tmpdirRspamdConf,
            "[domain]", "handler=mock", "mockstore=" + tmpdirRspamdConf + "/mockdns.json",
            "[domain:" + testdomain + "]", "dkim.mydkim=auto",
            "[dkim]", "handler=openssl", "keysize=2048",
            "[dkim:mydkim]", "keybasename=key", "keyname=dkimfile.key",
            "keylocation=" + tmpdirRspamdConf + "/dkim",
            "[service:rspamd]", "handler=rspamd", "dkim=mydkim", "reload=false",
            "signingconfdestinationfile=" + tmpdirRspamdConf + "/etc/rspamd/local.d/dkim_signing.conf",
            "signingconftemplatefile=" + tmpdirRspamdConf + "/dkim_signing_template.conf"])
        # a custom template to keep the test independent of the packaged
        # rspamd template (and its rspamd-specific syntax)
        os.makedirs(tmpdirRspamdConf, exist_ok=True)
        with open(os.path.join(tmpdirRspamdConf, "dkim_signing_template.conf"), 'w') as f:
            f.write('path = "{{ keyfile }}";\nselector = "{{ keyselector }}";\n')

        stdout = runCmd("python3 -m cryptdomainmgr --prepare --config-content '{}' 2>&1".format(conf))
        runCmd("python3 -m cryptdomainmgr --rollover --config-content '{}' 2>&1".format(conf))

        selectorMatch = re.search(r"add \(new\) DKIM for (key_\d+)\._domainkey\.", stdout)
        with self.subTest("check DNS record published with timestamped selector"):
            self.assertIsNotNone(selectorMatch)
        selector = selectorMatch.group(1)

        confFile = os.path.join(tmpdirRspamdConf, "etc", "rspamd", "local.d", "dkim_signing.conf")
        with self.subTest("check signing conf rendered by service handler"):
            self.assertTrue(os.path.isfile(confFile))
        with open(confFile) as f:
            confStr = f.read()
        with self.subTest("check conf contains deployed key path"):
            self.assertIn(os.path.join(tmpdirRspamdConf, "dkim", "dkimfile.key"), confStr)
        with self.subTest("check conf contains the same selector as the DNS record"):
            self.assertIn('selector = "{}"'.format(selector), confStr)
