#!/bin/bash

wget -O- https://rspamd.com/apt-stable/gpg.key | sudo apt-key add -
echo "deb http://rspamd.com/apt-stable/ $(lsb_release -cs) main" | sudo tee -a /etc/apt/sources.list.d/rspamd.list
apt update
apt install -y rspamd

