# Crypto Domain Manager

Cryptographic extensions for spam prevention and security should use periodically changing keys. Crypto Domain Manager automates all the steps.

This tool handles all dynamic (and static) domain administration and management work:

* It renews the certicate(s) using the dehydrated (letsencrypt) plugin.
* It generates the TLSA records and publishes it in DNS.
* It generates the DKIM keys using the rspamd plugin and publishes it in DNS.
* It retrieves and updates IPv4 and IPv6 entries with automatic IP lookup. (+ fixed IPs)
* It handles also: DMARC, SPF, SRV, CAA, ADSP.
* CAA can be set to "auto" to retrieve CA from cert configuration
* Records can be added or set (means overwrite existing).
* Wildcard and default handling implemented.
* That means coexitence with other handlers allowed.

Look at example.conf

* Multiple Configfiles with priority allowed
* Specify content of config file content as argument

## Idea behind

Updating keys, certifcates and other needs 3 steps to prevent gaps in availabillity:

1. **Prepare**: Create certificates, keys etc. and publish corresponding records to DNS.
2. **Rollover**: Apply new certificates and keys, because now negative cache TTL on DNS is reached.
3. **Cleanup**: Delete all no more needed stuff from disk and DNS.

## Needed Plugins and Dependencies

* **dnsuptools**: to interface with DNS API -- updating DNS entries
* **dehydrated**: to get new certificate (included with cryptdomainmgr)
* **rspamd**: to create (and use) DKIM keys

## Current compatibility

* **Domain**: inwx.de
* **Certificate**: letsencrypt.org
* **DKIM**: rspamd
* **Service**: systemd

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

* **Slides**: https://github.com/TheTesla/cryptdomainmgr-talk

* **Talks**: Wireless-Meshup 2018, GPN2018

## ToDo

* automated tests and deployment (continuous integration)
* nsupdate
* ARC key renewal
* WPIA integration
* deb package
* DNSSEC key renewal
* opendkim support
* service reload via init.d
* TXT record (may collide with SPF and other TXT based records)
* multi server support for one domain: TLSA delete by timeout
* contrain minimum renewal/phase time interval
* database backend
* monitoring
* run as service
* PowerDNS support

## Authors

**Stefan Helmert** all work on this projekt

## Want to support the project?

BURST: BURST-E56Y-7XQ7-C9E8-9XD55

GRC: Rzsny83yz7ReKd9k9cF4L5T4B1VB8GzzaT

CURE: BLLk87WviLrkAWZHT5eFSs7dStPXmHztDD

ETH: 0xA6a71817CC4E00B0646852401e9C5Cab024946d2

