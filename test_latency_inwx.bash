#!/bin/bash


python3 -m cryptdomainmgr --update test_inwxcreds.conf --config-content '[cdm] statedir=/tmp/test_cryptdomainmgr [domain] handler=dnsuptools/inwx [domain:test.entroserv.de] ip4=0.0.0.3,0.0.0.4 '

echo "$(date) - $(dig test.entroserv.de @ns.inwx.de +short | sed ':a;N;$!ba;s/\n/,/g')"

sleep 10

while [ True ] ; do echo "$(date) - $(dig test.entroserv.de @ns.inwx.de +short | sed ':a;N;$!ba;s/\n/,/g')" ; sleep 10 ; done


