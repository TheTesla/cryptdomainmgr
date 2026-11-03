#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2026 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

# Local end-to-end tests for the certificate handlers using the pebble
# ACME test server (https://github.com/letsencrypt/pebble).
#
# No internet access and no DNS provider credentials are needed:
# - certificates are issued by pebble (PEBBLE_VA_ALWAYS_VALID=1, the
#   dns-01 challenge is answered via the mock domain handler, pebble
#   does not verify it)
# - DNS updates go to the file-backed mock domain handler
#
# The pebble binary is looked up in this order:
#   1. PEBBLE_BIN environment variable
#   2. PATH
#   3. ~/.local/bin/pebble
# build: go install github.com/letsencrypt/pebble/v2/cmd/pebble@latest
# If pebble is not found, the tests are skipped.

import unittest
import json
import os
import shutil
import socket
import subprocess as sp
import time

from test.test_config import testdomain, testcertemail
from test.modules.complextests.test_certtlsa import tlsaFromCertFile
from cryptdomainmgr.modules.common.cdmprochelper import runCmd

tmpdir = "/tmp/test_cryptdomainmgr_pebble"
mockstore = os.path.join(tmpdir, "mockdns.json")
serverdir = "/tmp/test_cryptdomainmgr_pebble_server"

certname = "fullchain.pem"


def findPebble():
    cand = os.environ.get('PEBBLE_BIN')
    if cand and os.path.isfile(cand):
        return cand
    which = shutil.which('pebble')
    if which:
        return which
    home = os.path.join(os.path.expanduser('~'), '.local', 'bin', 'pebble')
    if os.path.isfile(home):
        return home
    return None


def freePort():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestCertPebble(unittest.TestCase):

    pebbleProc = None
    acmeURL = None
    caFile = None

    @classmethod
    def setUpClass(cls):
        pebbleBin = findPebble()
        if pebbleBin is None:
            raise unittest.SkipTest("pebble binary not found (set PEBBLE_BIN or install to ~/.local/bin)")
        shutil.rmtree(serverdir, ignore_errors=True)
        os.makedirs(serverdir, exist_ok=True)
        cls.caFile = os.path.join(serverdir, "wfe-cert.pem")
        keyFile = os.path.join(serverdir, "wfe-key.pem")
        sp.check_call(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-keyout", keyFile, "-out", cls.caFile,
                       "-days", "2", "-nodes", "-subj", "/CN=localhost",
                       "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"],
                      stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        port = freePort()
        config = {"pebble": {
            "listenAddress": "127.0.0.1:{}".format(port),
            "certificate": cls.caFile,
            "privateKey": keyFile,
            "httpPort": freePort(),
            "tlsPort": freePort(),
            "externalAccountBindingRequired": False,
            "domainBlocklist": [],
            "retryAfter": {"authz": 3, "order": 5}}}
        configFile = os.path.join(serverdir, "pebble-config.json")
        with open(configFile, "w") as f:
            json.dump(config, f)
        logFile = open(os.path.join(serverdir, "pebble.log"), "w")
        env = dict(os.environ, PEBBLE_VA_ALWAYS_VALID="1", PEBBLE_WFE_NONCEREJECT="0")
        cls.pebbleProc = sp.Popen([pebbleBin, "-config", configFile], env=env, stdout=logFile, stderr=sp.STDOUT)
        cls.acmeURL = "https://localhost:{}".format(port)
        deadline = time.time() + 20
        lastError = None
        while time.time() < deadline:
            if cls.pebbleProc.poll() is not None:
                raise RuntimeError("pebble exited early, log: {}".format(os.path.join(serverdir, "pebble.log")))
            try:
                sp.check_call(["curl", "-s", "-m", "2", "--cacert", cls.caFile, "-o", "/dev/null", cls.acmeURL + "/dir"],
                              stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                return
            except sp.CalledProcessError as e:
                lastError = e
                time.sleep(0.3)
        raise RuntimeError("pebble did not become ready ({}), log: {}".format(lastError, os.path.join(serverdir, "pebble.log")))

    @classmethod
    def tearDownClass(cls):
        if cls.pebbleProc is not None:
            cls.pebbleProc.terminate()
            try:
                cls.pebbleProc.wait(timeout=5)
            except sp.TimeoutExpired:
                cls.pebbleProc.kill()
                cls.pebbleProc.wait()

    def setUp(self):
        shutil.rmtree(tmpdir, ignore_errors=True)

    def cdmCmd(self, handler, phase, domainEntries, certEntries):
        content = "  ".join([
            "[cdm]", "statedir=" + tmpdir,
            "[domain]", "handler=mock", "mockstore=" + mockstore,
            "[domain:" + testdomain + "]"] + domainEntries + [
            "[cert]", "handler=" + handler, "email=" + testcertemail, "keysize=4096",
            "ca=" + self.acmeURL + "/dir", "caroot=" + self.caFile,
            "accountdir=" + os.path.join(tmpdir, "accounts"),
            "lockfile=" + os.path.join(tmpdir, "dehydrated.lock")] + certEntries)
        return "python3 -m cryptdomainmgr --{} --config-content '{}' 2>&1".format(phase, content)

    def runHandler(self, handler, subtestPrefix):
        dest = os.path.join(tmpdir, "ssl")
        certSection = ["[cert:mycert]", "destination=" + dest]
        stdout = runCmd(self.cdmCmd(handler, "prepare",
                                    ["cert=mycert", "tlsa.tcp.443=auto:3:1:1"], certSection))

        certFile = os.path.join(tmpdir, "modules", "cert", "mycert", "certs", testdomain, certname)
        with self.subTest(subtestPrefix + ": check cert file is created in tmp"):
            self.assertTrue(os.path.isfile(certFile))
        tlsa311 = tlsaFromCertFile(certFile, 3, 1, 1)
        with self.subTest(subtestPrefix + ": check add tlsa 3 1 1"):
            self.assertRegex(stdout, ".*add.*new.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain, tlsa311))

        runCmd(self.cdmCmd(handler, "rollover",
                           ["cert=mycert", "tlsa.tcp.443=auto:3:1:1"], certSection))
        with self.subTest(subtestPrefix + ": check cert file is copied to destination"):
            self.assertTrue(os.path.isfile(os.path.join(dest, testdomain, certname)))

        runCmd(self.cdmCmd(handler, "cleanup",
                           ["cert=mycert", "tlsa.tcp.443=auto:3:1:1"], certSection))
        with self.subTest(subtestPrefix + ": check current cert is not deleted"):
            self.assertTrue(os.path.isfile(certFile))

    def testHandlerDehydratedPebbleCreateCert(self):
        self.runHandler("dehydrated/pebble", "dehydrated")

    def testHandlerAcmePebbleCreateCert(self):
        self.runHandler("acme", "acme")
