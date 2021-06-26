#!/bin/bash

set -e

cd /cryptdomainmgr

echo "                                        "
echo "                                        "
echo "    Running cryptdomainmgr UPDATE       "
echo "----------------------------------------"
echo "                                        "

python3 -m cryptdomainmgr --update /etc/cryptdomainmgr/*

while [ True ]
do

  echo "                                        "
  echo "                                        "
  echo "    Running cryptdomainmgr PREPARE      "
  echo "----------------------------------------"
  echo "                                        "
  
  python3 -m cryptdomainmgr --prepare /etc/cryptdomainmgr/* --config-content "$1"
  
  echo "                                        "
  echo "                                        "
  echo "    Running cryptdomainmgr ROLLOVER     "
  echo "----------------------------------------"
  echo "                                        "
  
  python3 -m cryptdomainmgr --rollover /etc/cryptdomainmgr/* --config-content "$1"
  
  echo "                                        "
  echo "                                        "
  echo "    Running cryptdomainmgr CLEANUP      "
  echo "----------------------------------------"
  echo "                                        "
  
  python3 -m cryptdomainmgr --cleanup /etc/cryptdomainmgr/* --config-content "$1"

done

