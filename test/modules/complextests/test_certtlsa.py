#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest
import subprocess as sp
import os
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from test.test_config import testdomain, testns, tmpdir, testcertpath, testcertemail, INWXCREDSPRESENT, NOINWXCREDS, RUN_LIVE_STAGING, NOLIVESTAGING
from cryptdomainmgr.modules.common.cdmprochelper import runCmd



def tlsaFromCertFile(certFilename, certConstr = 3, keyOnly = 0, hashType = 1):
    with open(certFilename) as f:
        certCont = f.read()
    if 2 == int(certConstr) or 0 == int(certConstr):
        certCont = certCont.split('-----END CERTIFICATE-----')[1]
        certCont += '-----END CERTIFICATE-----'
    certObj = x509.load_pem_x509_certificate(certCont.encode())
    if 0 == int(keyOnly):
        ASN1 = certObj.public_bytes(serialization.Encoding.DER)
    else:
        ASN1 = certObj.public_key().public_bytes(serialization.Encoding.DER,
                                                 serialization.PublicFormat.SubjectPublicKeyInfo)
    if 1 == int(hashType):
        digest = hashes.Hash(hashes.SHA256())
    else:
        digest = hashes.Hash(hashes.SHA512())
    digest.update(ASN1)
    return digest.finalize().hex()

@unittest.skipUnless(INWXCREDSPRESENT and RUN_LIVE_STAGING, NOINWXCREDS if not INWXCREDSPRESENT else NOLIVESTAGING)
class TestCertTLSA(unittest.TestCase):
    def testMultiCertTLSACreate(self):
        stdout = runCmd("python3 -m cryptdomainmgr --prepare \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))


        tlsa311mycert = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert/certs",testdomain,"fullchain.pem"),3,1,1)
        tlsa311mycert2 = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert2/certs",testdomain,"fullchain.pem"),3,1,1)
        tlsa201mycert = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert/certs",testdomain,"fullchain.pem"),2,0,1)
        tlsa201mycert2 = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert2/certs",testdomain,"fullchain.pem"),2,0,1)

        with self.subTest("check add tlsa 3 1 1 mycert"):
            self.assertRegex(stdout, ".*add.*new.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert))
        with self.subTest("check add tlsa 3 1 1 mycert2"):
            self.assertRegex(stdout, ".*add.*new.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert2))
        with self.subTest("check add tlsa 2 0 1 mycert"):
            self.assertRegex(stdout, ".*add.*_443._tcp.{}.*2 0 1 {}.*".format(testdomain,tlsa201mycert))
        with self.subTest("check add tlsa 2 0 1 mycert2"):
            self.assertRegex(stdout, ".*add.*_443._tcp.{}.*2 0 1 {}.*".format(testdomain,tlsa201mycert2))

        stdout = runCmd("python3 -m cryptdomainmgr --rollover \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))

        #print(stdout)

        with self.subTest("check cert file exists - mycert"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath,testdomain,"fullchain.pem")))
        with self.subTest("check cert file exists - mycert2"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath+"2",testdomain,"fullchain.pem")))


        stdout = runCmd("python3 -m cryptdomainmgr --cleanup \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))


        stdout = runCmd("python3 -m cryptdomainmgr --prepare \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))

        stdout = runCmd("python3 -m cryptdomainmgr --rollover \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))

        stdout = runCmd("python3 -m cryptdomainmgr --cleanup \
                                 test_inwxcreds.conf --config-content \
        '\
        [cdm] \
        statedir={} \
        [domain] \
        handler=dnsuptools/inwx \
        [domain:{}] \
        cert=mycert,mycert2 \
        tlsa.tcp.443=auto:3:1:1,auto:2:0:1 \
        [cert] \
        handler=dehydrated/letsencrypt \
        email={} \
        keysize=4096 \
        [cert:mycert] \
        destination={} \
        extraflags=--staging,-x \
        [cert:mycert2] \
        destination={} \
        extraflags=--staging,-x \
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"))



        with self.subTest("check delete tlsa 3 1 1 mycert"):
            self.assertRegex(stdout, ".*delete.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert))
        with self.subTest("check delete tlsa 3 1 1 mycert2"):
            self.assertRegex(stdout, ".*delet.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert2))


