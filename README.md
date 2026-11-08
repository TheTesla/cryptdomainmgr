[![tests](https://github.com/TheTesla/cryptdomainmgr/actions/workflows/tests.yml/badge.svg)](https://github.com/TheTesla/cryptdomainmgr/actions/workflows/tests.yml)

# Crypto Domain Manager

Automate all your cryptographic needs!

* Automatic certificate renewal via ACME (LetsEncrypt or any ACMEv2 CA)
* DKIM key rotation with rspamd or OpenDKIM
* Automatic DNS record updates (TLSA, DKIM, CAA, DMARC, SPF, A/AAAA, MX, SRV, ...)
* Zero downtime: a prepare → rollover → cleanup phase model keeps old records valid while new ones propagate

Configure once and always stay up to date.

## Installation

Python 3.10 or newer is required.

```bash
# system libraries needed by dnsuptools (pycurl) and acme
apt install -y libcurl4-openssl-dev libssl-dev

# from PyPI
pip install cryptdomainmgr
```

or from a git checkout (poetry build):

```bash
git clone https://github.com/TheTesla/cryptdomainmgr
cd cryptdomainmgr
poetry build && pip install dist/cryptdomainmgr-*.whl
```

## Quickstart

Create a config file (or pass it via `--config-content`), then run the phases in order:

```ini
[cdm]
statedir=/var/lib/cryptdomainmgr

[domain]
handler=dnsuptools/inwx          # DNS provider: inwx credentials below

[domain:example.org]
cert=mycert                      # this domain uses certificate section "mycert"
tlsa.tcp.443=auto:3:1:1          # TLSA records derived automatically from the certificate

[cert]
handler=acme                     # ACME handler (see below)
email=you@example.org
keysize=4096
# ca=https://acme-staging-v02.api.letsencrypt.org/directory   # optional: staging

[cert:mycert]
destination=/etc/ssl/example.org
```

```bash
# credentials for the DNS API ([domain] user/passwd)
chmod 600 inwxcreds.conf         # format: [domain]\nuser=...\npasswd=...

cryptdomainmgr --update  inwxcreds.conf   # first run: static records (CAA, A/AAAA, ...)
cryptdomainmgr --prepare inwxcreds.conf   # create cert/keys, publish new TLSA/DKIM records
cryptdomainmgr --rollover inwxcreds.conf  # deploy cert/keys to destinations
cryptdomainmgr --cleanup inwxcreds.conf   # remove old records/files
```

Typically the first three phases are run weekly (e.g. via cron/systemd timer); `--update` is only needed for the initial run or changed static records. `--next` continues with the phase following the last completed one.

## Certificate handler

`[cert] handler=...`

| handler | description |
|---|---|
| `acme` (default) | ACMEv2 issuance using certbot's acme library. dns-01 challenges are published automatically through the configured domain handler. Config keys: `ca` (directory URL, default LetsEncrypt production), `caroot` (CA bundle for private/test CAs), `waitsec` (DNS propagation wait before answering challenges, default 9 s, retries with 3x backoff), `keysize`. Output layout is compatible with symlink-resolving consumers (cert.pem, fullchain.pem, chain.pem, privkey.pem). |

Legacy configurations with `handler=dehydrated/...` are automatically translated and served by the acme handler (`--staging` maps to the LetsEncrypt staging directory).

## DKIM handlers

`[dkim:<name>] handler=...` — generates the key pair, deploys it on rollover and publishes the public key as `<selector>._domainkey.<domain>` TXT (enable per domain with `dkim.<name>=auto`).

| handler | description |
|---|---|
| `openssl` (recommended) | local RSA key generation via the cryptography library, no external service and no sudo needed. Keys are written with mode 0600. |
| `rspamd` | key generation via `rspamadm dkim_keygen` and deployment with `_rspamd` ownership; for hosts where rspamd runs anyway. |

The selector is timestamped (`<keybasename>_<unixtime>`) so every rotation gets its own DNS record.

## DKIM signing services

The signing service config is rendered by the consuming SERVICE handler — the dkim handlers only provide key and selector:

```ini
# OpenDKIM (no rspamd required):
[service:opendkim]
handler=opendkim
dkim=mydkim                      # references [dkim:mydkim]
keytablefile=/etc/opendkim/KeyTable
signingtablefile=/etc/opendkim/SigningTable
reload=true                      # false when opendkim runs on another host/container

# rspamd:
[service:rspamd]
handler=rspamd
dkim=mydkim
signingconfdestinationfile=/etc/rspamd/local.d/dkim_signing.conf
signingconftemplatefile=/path/to/template.conf   # optional, a template is bundled
reload=true
```

Both render their service-specific configuration from the dkim section result (deployed key path + selector) on rollover and reload the service. See `exampleconf/example_dkim_opendkim.conf` for a complete example.

## DNS handlers

`[domain] handler=...`

| handler | description |
|---|---|
| `dnsuptools/inwx` | INWX DNS API (credentials via config file: `[domain] user=... passwd=...`) |
| `mock` | file-backed record store for testing, `mockstore=<path>` |

Supported record types per domain section: `ip4`, `ip6`, `mx`, `spf`, `dmarc`, `caa`, `srv`, `dkim`, `tlsa`, plus `acme` for ACME challenge tokens (managed automatically). See `exampleconf/example_tlsa.conf` for the syntax of each type.

## Service handlers

`[service:<name>] handler=...` — act on services after cert/dkim rollover:

| handler | reloads |
|---|---|
| `apache2`, `postfix`, `dovecot` | the respective systemd unit |
| `rspamd` | renders the DKIM signing config + reloads rspamd |
| `opendkim` | writes KeyTable/SigningTable + reloads opendkim |
| `traefik` | deploys certs into a traefik docker container |

## Testing

The test suite runs offline by default: live INWX tests are skipped unless a credentials file `test_inwxcreds.conf` exists, LetsEncrypt staging tests additionally need `CDM_LIVE_STAGING=1` (use sparingly). End-to-end certificate tests run against the local [pebble](https://github.com/letsencrypt/pebble) ACME server (`go install github.com/letsencrypt/pebble/v2/cmd/pebble@latest`, binary in `~/.local/bin` or `PEBBLE_BIN`).

```bash
python -m unittest discover                                  # offline suite
PEBBLE_BIN=~/.local/bin/pebble python -m unittest \
    test.modules.cert.test_cert_pebble                       # ACME e2e
```

## Documentation

* German project description and tutorial: https://www.entroserv.de/offene-software/cryptdomainmgr
* Slides: https://github.com/TheTesla/cryptdomainmgr-talk
* Example configurations: [exampleconf/](exampleconf/)
* hints:
  * Multiple config files with priority allowed
  * Config content can be passed as argument (`--config-content`)

## Next goals

* docker support - partly done, ToDo: label handling needed, daemon mode without external shell script needed
* website
* nsupdate for DNS updates

Long term goals:
* ARC key renewal
* DNSSEC key renewal
* multi server support for one domain: TLSA delete by timeout
* constrain minimum renewal/phase time interval
* validations - ensure signatures are used correctly
* run as service
* PowerDNS support

## Contributions

If you like the project feel free to give me a star.
Please let us know if you use this project.

All kind of contributions are welcome.
