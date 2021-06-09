[![Build Status](https://travis-ci.com/TheTesla/cryptdomainmgr.svg?branch=master)](https://travis-ci.com/TheTesla/cryptdomainmgr)

# Crypto Domain Manager

Automate all your cryptographic needs!

## Goals

* Zero downtime
* Automatic certificate renewal
* Spam protection
* Updated DNS records

Configure once and always stay up to date.

## Use cases

* Renew letsencrypt certicates
* Derive all kinds of data from the signature
* Ensure everything is secure

## External Service APIs

* Domain Certificate: [letsencrypt.org](https://letsencrypt.org)
* DNS Record Updates: [inwx.de](https://inwx.de)

## Linux Services

* DKIM signatures:
  * rspamd
* Reload systemd services:
  * apache2
  * postfix
  * dovecot
  * rspamd
  * traefik in Docker

## Managed DNS Records

* TLSA - for [DNS based authentication of named entities](https://en.wikipedia.org/wiki/DNS-based_Authentication_of_Named_Entities) DANE
* DKIM - domain keys for email signatures and spam detection
* CAA - specify the CA
* DMARC, SPF, ADSP - configure secure DNS

## No downtime strategy

Updating keys, certifcates and other needs 3 steps to prevent gaps in availabillity:

1. **Prepare**: Create certificates, keys etc. and publish corresponding records to DNS.
2. **Rollover**: Apply new certificates and keys, because now negative cache TTL on DNS is reached.
3. **Cleanup**: Delete all no more needed stuff from disk and DNS.

## Needed Plugins and Dependencies

* **dnsuptools**: to interface with DNS API -- updating DNS entries
* **dehydrated**: to get new certificate (included with cryptdomainmgr)
* **rspamd**: to create (and use) DKIM keys

## Installation

These libraries are needed for pycurl used by dnsuptools for automatic ip retrieving:
```bash
apt install -y libcurl4-openssl-dev libssl-dev
```
This comman is used by dehydrated to communicate with letsencrypt for certificate renewal:
```bash
apt install -y curl
```
For DKIM we need rspamd:
```bash
apt install -y lsb-release wget # optional
CODENAME=`lsb_release -c -s`
wget -O- https://rspamd.com/apt-stable/gpg.key | apt-key add -
echo "deb [arch=amd64] http://rspamd.com/apt-stable/ $CODENAME main" > /etc/apt/sources.list.d/rspamd.list
echo "deb-src [arch=amd64] http://rspamd.com/apt-stable/ $CODENAME main" >> /etc/apt/sources.list.d/rspamd.list
apt update
apt install -y rspamd
```
Now install the cryptdomainmgr. This pulls all need dependencies.
```bash
python2 -m pip install cryptdomainmgr
```
Feel free to try python3, but inwx client doesn't support it.
```bash
python3 -m pip install cryptdomainmgr
```

## Documentation

We need help here!

For now please look at:
* German project description and tutorial: https://www.entroserv.de/offene-software/cryptdomainmgr
* Slides: https://github.com/TheTesla/cryptdomainmgr-talk
* Look at the configfiles examples

hints:
* Multiple Configfiles with priority allowed
* Specify content of config file content as argument

## Next goals

* improve documentation
* docker support
* website
* automated tests
* nsupdate for DNS updates

Long term goals:
* ARC key renewal
* WPIA integration
* DNSSEC key renewal
* TXT record (may collide with SPF and other TXT based records)
* multi server support for one domain: TLSA delete by timeout
* constrain minimum renewal/phase time interval
* validations - ensure signatures are used correctly
* run as service
* PowerDNS support

## Contributions

If you like the project feel free to give me a star.
Please let us know if you use this project.

All kind of contributions are welcome.
