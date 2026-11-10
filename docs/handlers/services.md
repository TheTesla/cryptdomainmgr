# DKIM signing service handlers

Selected via `[service:<name>] handler=...`. The service handler renders its service-specific configuration from the dkim section result (deployed key path + selector) at rollover and reloads the service. The dkim handlers only provide the key – the config format is service knowledge and lives here.

Common config keys:

| key | default | description |
|---|---|---|
| `dkim` / `cert` | `auto` | references the `[dkim:<name>]` / `[cert:<name>]` section(s) to consume; also drives the `isReady` dependency |
| `reload` | `true` | reload the service after config deployment; set `false` when the service runs on another host or in a container |
| `certdestination` | – (disabled) | apache2/dovecot/postfix: pull the staged certificates of the referenced `cert=` sections into this directory at rollover (layout: `<certdestination>/<san>/`, same as the cert module deployment), before the reload |

## opendkim

Writes the [OpenDKIM](http://www.opendkim.org) KeyTable and SigningTable for **every domain whose domain section references the dkim section** and reloads opendkim.

| key | default | description |
|---|---|---|
| `keytablefile` | `/etc/opendkim/KeyTable` | KeyTable output path |
| `signingtablefile` | `/etc/opendkim/SigningTable` | SigningTable output path |

Generated entries (per domain):

```
# KeyTable
<selector>._domainkey.<domain> <domain>:<selector>:<keylocation>/<keyname>
# SigningTable
*@<domain> <selector>._domainkey.<domain>
```

The KeyTable references the **deployed** key location (`keylocation`/`keyname` from the dkim section), not the staging path – make sure the opendkim user can read it.

## Certificate pull for apache2 / dovecot / postfix

The systemd service handlers only reload the service – the certificates are normally deployed once by the cert module rollover (per `[cert:x] destination`) and referenced from the service's own config. Alternatively a service can pull the certificates itself into a service-specific directory:

```ini
[cert:mail]
# no destination needed for this certificate when only pulled services use it

[service:postfix]
handler=postfix
cert=mail
certdestination=/etc/postfix/ssl
```

At rollover (after the cert section is done – the `cert=` reference also drives the dependency wait) the staged cert/chain/fullchain/key files of every SAN are copied to `certdestination/<san>/` and the service is reloaded. Multiple cert sections can be referenced comma-separated; sections without a referenced cert section behave exactly as before.

## rspamd

Renders the rspamd DKIM signing config from the bundled template and reloads rspamd.

| key | default | description |
|---|---|---|
| `signingconfdestinationfile` | `/etc/rspamd/local.d/dkim_signing.conf` | output path of the rendered config |
| `signingconftemplatefile` | bundled template | Jinja2 template with `{{ keyfile }}` and `{{ keyselector }}` |

The bundled template sets `path`, `selector`, `use_esld = false` and `allow_username_mismatch = true` – override via `signingconftemplatefile` if you need more rspamd options.

## Complete examples

* OpenDKIM: [exampleconf/example_dkim_opendkim.conf](https://github.com/TheTesla/cryptdomainmgr/blob/master/exampleconf/example_dkim_opendkim.conf)

```ini
[domain:example.org]
dkim.mydkim=auto

[dkim:mydkim]
handler=openssl
keysize=2048
keybasename=key
keyname=dkimfile.key
keylocation=/var/lib/opendkim/keys

[service:opendkim]
handler=opendkim
dkim=mydkim
keytablefile=/etc/opendkim/KeyTable
signingtablefile=/etc/opendkim/SigningTable
reload=true
```

* rspamd: see `[service:rspamd]` in [exampleconf/example_tlsa.conf](https://github.com/TheTesla/cryptdomainmgr/blob/master/exampleconf/example_tlsa.conf)
