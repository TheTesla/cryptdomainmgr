# Certificate handlers

Selected via `[cert] handler=...`.

## acme (default)

ACMEv2 certificate issuance using [certbot's acme library](https://github.com/certbot/certbot).

!!! note "Legacy configurations"
    Configurations with `handler=dehydrated/...` are automatically translated and served by the acme handler: `--staging` in `extraflags` maps to the LetsEncrypt staging directory, non-letsencrypt CA names clear the CAA default. New configurations should use `handler=acme` directly.

### Config keys

| key | default | description |
|---|---|---|
| `ca` | LetsEncrypt production directory | ACME directory URL, e.g. `https://acme-staging-v02.api.letsencrypt.org/directory` for LetsEncrypt staging (untrusted test certificates, no production rate limits) |
| `caroot` | system trust store | CA bundle (PEM) to verify the ACME server; required for private/test CAs like pebble |
| `keysize` | 4096 | RSA key size for the certificate key |
| `email` | – | account contact email, required |
| `waitsec` | 9 | DNS propagation wait in seconds before the dns-01 challenge is answered |
| `extraflags` | – | kept for compatibility, only non-dehydrated flags are passed through |

### Behaviour

* dns-01 challenges are published automatically: for every domain in the certificate the handler calls the configured domain handler (`cryptdomainmgr --update` mechanism in-process), the challenge TXT records are written with **TTL 300** (the minimum the INWX API accepts) to avoid stale resolver caches when several certificates share one domain.
* On validation failure the handler retries with a fresh order and an exponential propagation wait (9 → 27 → 81 → 243 s) – an invalid authorization invalidates the whole order, so each retry re-orders and re-publishes new tokens.
* Account keys are persisted per cert section and re-used (idempotent registration).
* Output layout per domain: `cert.pem`, `fullchain.pem`, `chain.pem`, `privkey.pem` – timestamped files with stable symlinks, so downstream consumers that resolve symlinks keep working across renewals.

### Example

```ini
[cert]
handler=acme
email=you@example.org
keysize=4096

[cert:mycert]
destination=/etc/ssl/example.org
```

For LetsEncrypt staging add `ca=https://acme-staging-v02.api.letsencrypt.org/directory` to the `[cert]` section (see `exampleconf/example_acme.conf`).
