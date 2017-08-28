#!/bin/bash

# inxwupdate.bash inwxapi inwxlogin inwxpasswd name tld ipv4 ipv6 dkimkey ttl

domain=$4.$5

python /root/inwx-client/update_ns_record.py "$1" "$2" "$3" "del" "$4" "$5"
python /root/inwx-client/update_ns_record.py "$1" "$2" "$3" "add" "$4" "$5" "A" "$6" $9
python /root/inwx-client/update_ns_record.py "$1" "$2" "$3" "add" "$4" "$5" "AAAA" "$7" $9
python /root/inwx-client/update_ns_record.py "$1" "$2" "$3" "add" "$4" "$5" "MX" "$domain" $9
python /root/inwx-client/update_ns_record.py "$1" "$2" "$3" "add" "$4" "$5" "TXT" "v=spf1 a:$domain ?all" $9
python /root/inwx-client/update_ns_record.py "$1" "$2" "$3" "del" "key1._domainkey.$4" "$5"
python /root/inwx-client/update_ns_record.py "$1" "$2" "$3" "add" "key1._domainkey.$4" "$5" "TXT" "$8" $9
 




