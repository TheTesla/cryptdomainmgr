# Configuration

## Sources and priority

Multiple config files are allowed and are merged with priority (later files / later sections override earlier ones):

```bash
cryptdomainmgr --prepare base.conf overrides.conf
```

Config content can also be passed directly as an argument (double spaces become line breaks):

```bash
cryptdomainmgr --prepare --config-content '[cdm]  statedir=/tmp/cdm  [domain]  handler=dnsuptools/inwx'
```

## Section layout

| section | purpose |
|---|---|
| `[cdm]` | global settings: `statedir` (state and staging files) |
| `[domain:<domain>]` | DNS records of a domain, references cert/dkim sections |
| `[cert]` / `[cert:<name>]` | certificate issuance, `[cert]` holds defaults for all named sections |
| `[dkim]` / `[dkim:<name>]` | DKIM key generation |
| `[service:<name>]` | services consuming certs/keys (reload, config rendering) |

`DEFAULT` sections define defaults inherited by the named sections of the same module.

## Cross references

Sections reference each other by name:

```ini
[domain:example.org]
cert=mycert          # TLSA records are derived from this cert section
dkim.mydkim=auto     # DKIM public key of [dkim:mydkim] is published

[service:opendkim]
dkim=mydkim          # the service consumes this dkim section
```

Referenced sections that do not exist produce a warning and are skipped.

## Credentials

DNS API credentials (`[domain] user=... passwd=...`) belong in a separate file with mode 600, referenced on the command line. The file is never committed (the repo ships only an encrypted example). Credentials never appear on the command line of handler calls – the acme handler publishes challenge records in-process.
