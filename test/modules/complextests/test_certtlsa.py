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
from OpenSSL import crypto
import hashlib
from test.test_config import testdomain, testns, tmpdir, testcertpath, testcertemail



def tlsaFromCertFile(certFilename, certConstr = 3, keyOnly = 0, hashType = 1):
    #certCont = sp.check_output(('cat', str(certFilename)))
    with open(certFilename) as f:
        certCont = f.read()
    if 2 == int(certConstr) or 0 == int(certConstr):
        certCont = certCont.split('-----END CERTIFICATE-----')[1]
        certCont += '-----END CERTIFICATE-----'
    #ps = sp.Popen(('echo', '-e', certCont), stdout=sp.PIPE)
    certObj = crypto.load_certificate(crypto.FILETYPE_PEM, certCont)
    if 0 == int(keyOnly):
        #ps = sp.Popen(('openssl', 'x509', '-outform', 'DER'), stdout=sp.PIPE, stdin=ps.stdout)
        ASN1 = crypto.dump_certificate(crypto.FILETYPE_ASN1, certObj)
    else:
        #ps = sp.Popen(('openssl', 'x509', '-pubkey', '-noout'), stdout=sp.PIPE, stdin=ps.stdout)
        #ps = sp.Popen(('openssl', 'pkey', '-pubin', '-outform', 'DER'), stdin=ps.stdout, stdout=sp.PIPE)
        pubKeyObj = certObj.get_pubkey()
        ASN1 = crypto.dump_publickey(crypto.FILETYPE_ASN1, pubKeyObj)
    if 1 == int(hashType):
        #output = sp.check_output(('openssl', 'sha256'), stdin=ps.stdout).split(b' ')[1].replace(b'\n',b'')
        output = hashlib.sha256(ASN1).hexdigest()
    elif 2 == int(hashType):
        #output = sp.check_output(('openssl', 'sha512'), stdin=ps.stdout).split(b' ')[1].replace(b'\n',b'')
        output = hashlib.sha512(ASN1).hexdigest()
    return output.encode()

class TestCertTLSA(unittest.TestCase):
    def testMultiCertTLSACreate(self):
        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
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
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)


        tlsa311mycert = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert/certs",testdomain,"fullchain.pem"),3,1,1)
        tlsa311mycert2 = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert2/certs",testdomain,"fullchain.pem"),3,1,1)
        tlsa201mycert = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert/certs",testdomain,"fullchain.pem"),2,0,1)
        tlsa201mycert2 = tlsaFromCertFile(os.path.join(tmpdir,"modules/cert/mycert2/certs",testdomain,"fullchain.pem"),2,0,1)

        stdout = str(stdout, "utf-8")
        with self.subTest("check add tlsa 3 1 1 mycert"):
            self.assertRegex(stdout, ".*add.*new.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert))
        with self.subTest("check add tlsa 3 1 1 mycert2"):
            self.assertRegex(stdout, ".*add.*new.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert2))
        with self.subTest("check add tlsa 2 0 1 mycert"):
            self.assertRegex(stdout, ".*add.*_443._tcp.{}.*2 0 1 {}.*".format(testdomain,tlsa201mycert))
        with self.subTest("check add tlsa 2 0 1 mycert2"):
            self.assertRegex(stdout, ".*add.*_443._tcp.{}.*2 0 1 {}.*".format(testdomain,tlsa201mycert2))

        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
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
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)

        #print(stdout)

        with self.subTest("check cert file exists - mycert"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath,testdomain,"fullchain.pem")))
        with self.subTest("check cert file exists - mycert2"):
            self.assertTrue(os.path.isfile(os.path.join(testcertpath+"2",testdomain,"fullchain.pem")))


        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
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
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)


        stdout = sp.check_output("python3 -m cryptdomainmgr --prepare \
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
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --rollover \
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
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)

        stdout = sp.check_output("python3 -m cryptdomainmgr --cleanup \
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
        ' 2>&1".format(tmpdir,testdomain,testcertemail,testcertpath,testcertpath+"2"), shell=True)



        stdout = str(stdout, "utf-8")
        with self.subTest("check delete tlsa 3 1 1 mycert"):
            self.assertRegex(stdout, ".*delete.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert))
        with self.subTest("check delete tlsa 3 1 1 mycert2"):
            self.assertRegex(stdout, ".*delet.*_443._tcp.{}.*3 1 1 {}.*".format(testdomain,tlsa311mycert2))


