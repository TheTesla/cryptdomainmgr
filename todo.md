# enhancements of existing functions

* TLSA: generate tlsa records only for a specific certificate, if multiple certificates are given for domain by specifying cert name instead of auto for tlsa record
* replace dehydrated by python based ACME framework
  * solve problem: changed cert parameters must force renew cert
* function for systemctl reload to be modular for other non systemd versions (and SIGHUP based service reload)
* generate dkim key by openssl
* raise exceptions when error
* more docker automatism: cert labels
* docker (SIGHUP based service reload)
  * rspamd
  * postfix
  * dovecot
* include config
* daemon mode handling renew cycle timing
* config includes
* multiple direct argument configs
* "become" option for sudo etc.


# Tests

* DKIM
* function for calling cryptdomainmgr program
* propagate errors for calling cryptdomainmgr in tests
* SOA record

