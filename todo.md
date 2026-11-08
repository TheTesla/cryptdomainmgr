# enhancements of existing functions

* TLSA: generate tlsa records only for a specific certificate, if multiple certificates are given for domain by specifying cert name instead of auto for tlsa record
* function for systemctl reload to be modular for other non systemd versions (and SIGHUP based service reload)
* raise exceptions when error (servicehelper raises a string instead of an exception)
* more docker automatism: cert labels
* docker (SIGHUP based service reload)
  * rspamd
  * postfix
  * dovecot
  * opendkim
* include config
* daemon mode handling renew cycle timing
* config includes
* multiple direct argument configs
* "become" option for sudo etc.
* dkim: configurable key owner (user/group) for the openssl handler deployments

# done (2026)

* ~~replace dehydrated by python based ACME framework~~ -> acme handler (certbot's acme library), dehydrated removed
* ~~generate dkim key by openssl~~ -> openssl dkim handler (cryptography library)
* ~~DKIM signing config rendering in the service handlers~~ -> rspamd/opendkim service handlers
* ~~GitHub Actions CI/CD~~ -> tests workflow + release workflow (PyPI, docker)

# Tests

* DKIM
* function for calling cryptdomainmgr program
* propagate errors for calling cryptdomainmgr in tests
* SOA record
