#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import unittest

from cryptdomainmgr.cdmconfighandler import ConfigReader

def procConfig(cr):
    cr.open()
    cr.interprete(None)
    return cr

class TestDomainconfighandler(unittest.TestCase):
    def testNoSection(self):
        cr = ConfigReader()
        cr.setContentList([''])
        procConfig(cr)
        self.assertEqual(cr.config, {})

    def testDomainDefaultSection(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]'])
        procConfig(cr)
        self.assertEqual({'ip4AggrAdd': [], 'ip4AggrDel': [], 'ip6AggrAdd': [], 'ip6AggrDel': [], 'dkimAggrAdd': [], 'dkimAggrDel': [], 'tlsaAggrAdd': [], 'tlsaAggrDel': [], 'mxAggrAdd': [], 'mxAggrDel': [], 'srvAggrAdd': [], 'srvAggrDel': [], 'caaAggrAdd': [], 'caaAggrDel': [], 'spfAggrAdd': set(), 'spfAggrDel': set()}, cr.config['domain']['DEFAULT'])

    def testDomainDefaultSectionIP4set(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nip4=0.0.0.0 , auto '])
        procConfig(cr)
        self.assertEqual([{'content': '0.0.0.0'}, {'content': 'auto'}], cr.config['domain']['DEFAULT']['ip4AggrAdd'])
        self.assertEqual([{}, {}], cr.config['domain']['DEFAULT']['ip4AggrDel'])

    def testDomainDefaultSectionIP4add(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nip4 + = 0.0.0.0'])
        procConfig(cr)
        self.assertEqual([{'content': '0.0.0.0'}], cr.config['domain']['DEFAULT']['ip4AggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['ip4AggrDel'])

    def testDomainNamedSectionIP6set(self):
        cr = ConfigReader()
        cr.setContentList(['[domain:mydomain.de]\nip6  =   123::0000:46ef  '])
        procConfig(cr)
        self.assertEqual([{'content': '123::0000:46ef'}], cr.config['domain']['mydomain.de']['ip6AggrAdd'])
        self.assertEqual([{}], cr.config['domain']['mydomain.de']['ip6AggrDel'])

    def testDomainDefaultSectionIP6add(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nip6 + = [123::0000:46ef]'])
        procConfig(cr)
        self.assertEqual([{'content': '[123::0000:46ef]'}], cr.config['domain']['DEFAULT']['ip6AggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['ip6AggrDel'])

    def testDomainDefaultSectionMXset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nmx = mx0.domain, mx1.domain:20\nmx.30 = mx2.domain:15\nmx.40 = mx3.domain '])
        procConfig(cr)
        self.assertEqual([{'content': 'mx0.domain', 'prio': '10'}, {'content': 'mx1.domain', 'prio': '20'}, {'content': 'mx2.domain', 'prio': '15'}, {'content': 'mx3.domain', 'prio': '40'}], cr.config['domain']['DEFAULT']['mxAggrAdd'])
        self.assertEqual([{}, {}, {'prio': '30'}, {'prio': '40'}], cr.config['domain']['DEFAULT']['mxAggrDel'])

    def testDomainDefaultSectionMXadd(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nmx + = mx0.domain, mx1.domain:20\nmx.30 + = mx2.domain:15\nmx.40 + = mx3.domain  '])
        procConfig(cr)
        self.assertEqual([{'content': 'mx0.domain', 'prio': '10'}, {'content': 'mx1.domain', 'prio': '20'}, {'content': 'mx2.domain', 'prio': '15'}, {'content': 'mx3.domain', 'prio': '40'}], cr.config['domain']['DEFAULT']['mxAggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['mxAggrDel'])

    def testDomainDefaultSectionSRVset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nsrv.service.proto.port.weight.prio  = testsrv.entroserv.de:PRIO:WEIGHT:PORT:PROTO:SERVICE  '])
        procConfig(cr)
        self.assertEqual([{'server': 'testsrv.entroserv.de', 'service': 'SERVICE', 'proto': 'PROTO', 'port': 'PORT', 'weight': 'WEIGHT', 'prio': 'PRIO'}], cr.config['domain']['DEFAULT']['srvAggrAdd'])
        self.assertEqual([{'service': 'service', 'proto': 'proto', 'port': 'port', 'weight': 'weight', 'prio': 'prio'}], cr.config['domain']['DEFAULT']['srvAggrDel'])

    def testDomainDefaultSectionSRVadd(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nsrv.service.proto.port.weight.prio + = testsrv.entroserv.de:PRIO:WEIGHT:PORT:PROTO:SERVICE   '])
        procConfig(cr)
        self.assertEqual([{'server': 'testsrv.entroserv.de', 'service': 'SERVICE', 'proto': 'PROTO', 'port': 'PORT', 'weight': 'WEIGHT', 'prio': 'PRIO'}], cr.config['domain']['DEFAULT']['srvAggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['srvAggrDel'])

    def testDomainDefaultSectionCAAset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ncaa  = auto,   myflag    mytag    myca.caa  \ncaa.a.b.c  =  d  e  f '])
        procConfig(cr)
        self.assertEqual([{'flag': 'auto'}, {'flag': 'myflag', 'tag': 'mytag', 'url': 'myca.caa'}, {'flag': 'd', 'tag': 'f', 'url': 'a'}], cr.config['domain']['DEFAULT']['caaAggrAdd'])
        self.assertEqual([{},{},{'tag': 'b', 'url': 'a'}], cr.config['domain']['DEFAULT']['caaAggrDel'])

    def testDomainDefaultSectionCAAadd(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ncaa + = auto, myflag  mytag myca.caa  '])
        procConfig(cr)
        self.assertEqual([{'flag': 'auto'}, {'flag': 'myflag', 'tag': 'mytag', 'url': 'myca.caa'}], cr.config['domain']['DEFAULT']['caaAggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['caaAggrDel'])

    def testDomainDefaultSectionSPFset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nspf  = +mx ,  -ip4 ,  ip6 ,  ?all '])
        procConfig(cr)
        self.assertEqual({'+mx', '-ip4', 'ip6', '?all'}, cr.config['domain']['DEFAULT']['spfAggrAdd'])
        self.assertEqual({'*'}, cr.config['domain']['DEFAULT']['spfAggrDel'])

    def testDomainDefaultSectionSPFadd(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nspf  + = +mx ,  -ip4 ,  ip6 ,  ?all '])
        procConfig(cr)
        self.assertEqual({'+mx', '-ip4', 'ip6', '?all'}, cr.config['domain']['DEFAULT']['spfAggrAdd'])
        self.assertEqual(set(), cr.config['domain']['DEFAULT']['spfAggrDel'])

    def testDomainDefaultSectionSPFdel(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nspf  - = +mx ,  -ip4 ,  ip6 ,  ?all '])
        procConfig(cr)
        self.assertEqual(set(), cr.config['domain']['DEFAULT']['spfAggrAdd'])
        self.assertEqual({'+mx', '-ip4', 'ip6', '?all'}, cr.config['domain']['DEFAULT']['spfAggrDel'])

    def testDomainDefaultSectionDMARCset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ndmarc  = \ndmarc.p = quarantine \ndmarc.dummy = blub'])
        procConfig(cr)
        self.assertEqual({'': '', 'p': 'quarantine', 'dummy': 'blub'}, cr.config['domain']['DEFAULT']['dmarc'])

    def testDomainDefaultSectionSOAset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nsoa  = \nsoa.a = x \nsoa.b = blub'])
        procConfig(cr)
        self.assertEqual({'': '', 'a': 'x', 'b': 'blub'}, cr.config['domain']['DEFAULT']['soa'])

    def testDomainDefaultSectionDMARCsetPart(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ndmarc.p = quarantine \ndmarc.dummy = blub'])
        procConfig(cr)
        self.assertEqual({'p': 'quarantine', 'dummy': 'blub'}, cr.config['domain']['DEFAULT']['dmarc'])

    def testDomainDefaultSectionADSPset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nadsp  = all '])
        procConfig(cr)
        self.assertEqual('all', cr.config['domain']['DEFAULT']['adsp'])

    def testDomainDefaultSectionACMEset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nacme  = qwertz '])
        procConfig(cr)
        self.assertEqual('qwertz', cr.config['domain']['DEFAULT']['acme'])

    def testDomainDefaultSectionDKIMset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ndkim  = auto:maindkim , auto2:extradkim \ndkim.extdkim = auto3'])
        procConfig(cr)
        self.assertEqual([{'op':'auto', 'content':'maindkim'}, {'op': 'auto2', 'content': 'extradkim'}, {'content': 'extdkim', 'op': 'auto3'}], cr.config['domain']['DEFAULT']['dkimAggrAdd'])
        self.assertEqual([{},{},{'content':'extdkim'}], cr.config['domain']['DEFAULT']['dkimAggrDel'])

    def testDomainDefaultSectionDKIMset2(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\n dkim.extradkim = auto2 , auto3 \ndkim = auto4:maindkim2 '])
        procConfig(cr)
        self.assertEqual([{'op': 'auto2', 'content': 'extradkim'}, {'op': 'auto3', 'content': 'extradkim'}, {'op': 'auto4', 'content': 'maindkim2'}], cr.config['domain']['DEFAULT']['dkimAggrAdd'])
        self.assertEqual([{'content': 'extradkim'}, {'content': 'extradkim'}, {}], cr.config['domain']['DEFAULT']['dkimAggrDel'])

    def testDomainDefaultSectionDKIMadd(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ndkim +  = auto:maindkim '])
        procConfig(cr)
        self.assertEqual([{'op':'auto', 'content':'maindkim'}], cr.config['domain']['DEFAULT']['dkimAggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['dkimAggrDel'])

    def testDomainDefaultSectionDKIMadd2(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ndkim.maindkim +  = auto '])
        procConfig(cr)
        self.assertEqual([{'op':'auto', 'content':'maindkim'}], cr.config['domain']['DEFAULT']['dkimAggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['dkimAggrDel'])

    def testDomainDefaultSectionTLSAset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ntlsa  = auto:3:1:1:443:tcp , auto2:2:0:1:143:udp \ntlsa.icmp.80.*.1.3 = auto3'])
        procConfig(cr)
        self.assertEqual([{'op': 'auto', 'proto': 'tcp', 'port': '443', 'matchingtype': '1', 'selector': '1', 'usage': '3'}, {'op': 'auto2', 'proto': 'udp', 'port': '143', 'matchingtype': '1', 'selector': '0', 'usage': '2'}, {'op': 'auto3', 'proto': 'icmp', 'port': '80', 'selector': '1', 'usage': '3'}], cr.config['domain']['DEFAULT']['tlsaAggrAdd'])
        self.assertEqual([{}, {}, {'proto': 'icmp', 'port': '80', 'selector': '1', 'usage': '3'}], cr.config['domain']['DEFAULT']['tlsaAggrDel'])

    def testDomainDefaultSectionTLSAadd(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ntlsa  + = auto:3:1:1:443:tcp , auto2:2:0:1:143:udp \ntlsa.icmp.80.0.1.3  + = auto3'])
        procConfig(cr)
        self.assertEqual([{'op': 'auto', 'proto': 'tcp', 'port': '443', 'matchingtype': '1', 'selector': '1', 'usage': '3'}, {'op': 'auto2', 'proto': 'udp', 'port': '143', 'matchingtype': '1', 'selector': '0', 'usage': '2'}, {'op': 'auto3', 'proto': 'icmp', 'port': '80', 'matchingtype': '0', 'selector': '1', 'usage': '3'}], cr.config['domain']['DEFAULT']['tlsaAggrAdd'])
        self.assertEqual([], cr.config['domain']['DEFAULT']['tlsaAggrDel'])

    def testDomainDefaultSectionCertset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\ncert  = noocsp , withocsp'])
        procConfig(cr)
        self.assertEqual(['noocsp', 'withocsp'], cr.config['domain']['DEFAULT']['cert'])

    def testDomainDefaultSectionHandlerset(self):
        cr = ConfigReader()
        cr.setContentList(['[domain]\nhandler  = dnsuptools/inwx \nuser = myuser \npasswd = mypasswd '])
        procConfig(cr)
        self.assertEqual({'handler': 'dnsuptools/inwx', 'user': 'myuser', 'passwd': 'mypasswd', 'accessparams': ['handler', 'user', 'passwd']}, {k: cr.config['domain']['DEFAULT'][k] for k in ['handler', 'user', 'passwd', 'accessparams']})

if "__main__" == __name__:
    unittest.main()


