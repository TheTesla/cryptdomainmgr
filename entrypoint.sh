#!/bin/bash

INTERVAL=86400

set -e

cd /cryptdomainmgr

echo "                                        "
echo "                                        "
echo "    Running cryptdomainmgr UPDATE       "
echo "----------------------------------------"
echo "                                        "

python3 -m cryptdomainmgr --update /etc/cryptdomainmgr/*

echo "                                        "
echo "                                        "
echo "    Running cryptdomainmgr PREPARE      "
echo "----------------------------------------"
echo "                                        "

python3 -m cryptdomainmgr --prepare /etc/cryptdomainmgr/*

echo "                                        "
echo "                                        "
echo "    Running cryptdomainmgr ROLLOVER     "
echo "----------------------------------------"
echo "                                        "

python3 -m cryptdomainmgr --rollover /etc/cryptdomainmgr/*

echo "                                        "
echo "                                        "
echo "    Running cryptdomainmgr CLEANUP      "
echo "----------------------------------------"
echo "                                        "

python3 -m cryptdomainmgr --cleanup /etc/cryptdomainmgr/*


while [ True ]
do

  echo "Waiting $INTERVAL seconds."
  sleep $INTERVAL

  echo "                                        "
  echo "                                        "
  echo "    Running cryptdomainmgr PREPARE      "
  echo "----------------------------------------"
  echo "                                        "
  
  python3 -m cryptdomainmgr --prepare /etc/cryptdomainmgr/*
  

  echo "Waiting $INTERVAL seconds."
  sleep $INTERVAL

  echo "                                        "
  echo "                                        "
  echo "    Running cryptdomainmgr ROLLOVER     "
  echo "----------------------------------------"
  echo "                                        "
  
  python3 -m cryptdomainmgr --rollover /etc/cryptdomainmgr/*
  
  echo "Waiting $INTERVAL seconds."
  sleep $INTERVAL

  echo "                                        "
  echo "                                        "
  echo "    Running cryptdomainmgr CLEANUP      "
  echo "----------------------------------------"
  echo "                                        "
  
  python3 -m cryptdomainmgr --cleanup /etc/cryptdomainmgr/*

done

