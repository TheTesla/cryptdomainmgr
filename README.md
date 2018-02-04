# Crypto Domain Manager

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

