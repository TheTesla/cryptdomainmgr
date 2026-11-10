# DKIM key handlers

Selected via `[dkim:<name>] handler=...`. The handler generates the key pair, deploys it on rollover to `keylocation/keyname` and publishes the public key as `<selector>._domainkey.<domain>` TXT record (enabled per domain with `dkim.<name>=auto`).

The selector is timestamped (`<keybasename>_<unixtime>`), so every rotation gets its own DNS record. The signing **service** config is rendered by the consuming [service handler](services.md), not by the dkim handler.

## openssl (recommended)

Local RSA key generation via the [cryptography](https://cryptography.io) library. No external service and no sudo needed – suitable for containers and CI.

| key | default | description |
|---|---|---|
| `keysize` | 2048 | RSA key size |
| `keybasename` | `key` | selector prefix |
| `keylocation` | `/var/lib/rspamd/dkim` | deployment directory (rollover) |
| `keyname` | `dkim.key` | deployment file name |

The private key is written with mode 0600.

## rspamd

Key generation via `rspamadm dkim_keygen` and deployment with `_rspamd:_rspamd` ownership (sudo). Use this on hosts where rspamd runs anyway and should keep the ownership convention.

Same config keys as the openssl handler.

## DNS publication

Enable per domain section:

```ini
[domain:example.org]
dkim.mydkim=auto       # publishes the public key of [dkim:mydkim]
```

The published TXT record has the form `v=DKIM1; k=rsa; p=<base64 DER SubjectPublicKeyInfo>`.
