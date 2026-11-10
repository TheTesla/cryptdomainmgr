[![tests](https://github.com/TheTesla/cryptdomainmgr/actions/workflows/tests.yml/badge.svg)](https://github.com/TheTesla/cryptdomainmgr/actions/workflows/tests.yml)
[![docs](https://github.com/TheTesla/cryptdomainmgr/actions/workflows/docs.yml/badge.svg)](https://github.com/TheTesla/cryptdomainmgr/actions/workflows/docs.yml)

# Crypto Domain Manager

Automate all your cryptographic needs!

* Automatic certificate renewal via ACME (LetsEncrypt or any ACMEv2 CA)
* DKIM key rotation with rspamd or OpenDKIM
* Automatic DNS record updates (TLSA, DKIM, CAA, DMARC, SPF, A/AAAA, MX, SRV, ...)
* Zero downtime: a **prepare → rollover → cleanup** phase model keeps old records valid while new ones propagate

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
handler=acme                     # ACME handler
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

## Documentation

The full documentation lives in [`docs/`](docs/index.md) (built with MkDocs Material, deployed via GitHub Pages):

* **[Handler reference](docs/handlers/cert.md)** – certificate (ACME), DKIM key handlers, signing services (OpenDKIM/rspamd), DNS handlers with all config keys
* **[Configuration](docs/config.md)** – config sources, priority, cross references, credentials
* **[Architecture](docs/architecture.md)** – phase model, handler dispatch, fallbacks, state handling
* **[Testing](docs/testing.md)** – offline suite, pebble e2e, live test gates

Example configurations: [exampleconf/](exampleconf/)

Build the docs locally: `pip install mkdocs-material && mkdocs serve`

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
