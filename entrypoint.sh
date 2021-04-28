#!/bin/bash

set -e

cd /cryptdomainmgr

echo "                                        "
echo "    Running cryptdomainmgr UPDATE       "
echo "----------------------------------------"

python3 -m cryptdomainmgr --update /etc/cryptdomainmgr/*

echo "                                        "
echo "    Running cryptdomainmgr PREPARE      "
echo "----------------------------------------"

python3 -m cryptdomainmgr --prepare /etc/cryptdomainmgr/*

echo "                                        "
echo "    Running cryptdomainmgr ROLLOVER     "
echo "----------------------------------------"

python3 -m cryptdomainmgr --rollover /etc/cryptdomainmgr/*

echo "                                        "
echo "    Running cryptdomainmgr CLEANUP      "
echo "----------------------------------------"

python3 -m cryptdomainmgr --cleanup /etc/cryptdomainmgr/*

