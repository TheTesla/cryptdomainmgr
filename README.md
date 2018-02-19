# Crypto Domain Manager

Cryptographic extensions for spam prevention and security should use periodically changing keys. Crypto Domain Manager automates all the steps.

This tool handles all dynamic (and static) domain administration and management work:

* It renews the certicate(s) using the letsencrypt plugin.
* It generates the TLSA records and publishes it in DNS.
* It generates the DKIM keys using the rspamd plugin and publishes it in DNS.
* It retrieves and updates IPv4 and IPv6 entries with automatic IP lookup. (+ fixed IPs)
* It handles also: DMARC, SPF, SRV, CAA, ADSP.
* Records can be added or set (means overwrite existing).
* Wildcard and default handling implemented.
* That means coexitence with other handlers allowed.

Look at examplenew.conf

* Multiple Configfiles with priority allowed


## Idea behind

Updating keys, certifcates and other needs 3 steps to prevent gaps in availabillity:

1. **Prepare**: Create certificates, keys etc. and publish corresponding records to DNS.
2. **Rollover**: Apply new certificates and keys, because now negative cache TTL on DNS is reached.
3. **Cleanup**: Delete all no more needed stuff from disk and DNS.


## Needed Plugins and Dependencies

* **dnsuptools**: to interface with DNS API -- updating DNS entries
* **certbot**: to get new certificate
* **rspamd**: to create (and use) DKIM keys

## Authors

**Stefan Helmert** all work on this projekt
