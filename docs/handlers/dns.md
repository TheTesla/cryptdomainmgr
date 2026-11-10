# DNS handlers

Selected via `[domain] handler=...`. DNS handlers publish all record types of the domain sections and the automatically derived records (TLSA from certificates, DKIM public keys, ACME challenge tokens).

## dnsuptools/inwx

Uses the [dnsuptools](https://github.com/TheTesla/dnsuptools) library with the INWX XML-RPC API.

Credentials are supplied via a config file referenced on the command line:

```ini
# inwxcreds.conf - keep at mode 600, never commit
[domain]
user=your-inwx-user
passwd=your-inwx-password
```

!!! warning "TTL constraints"
    The INWX API accepts TTLs between 300 and 2764800 seconds. ACME challenge TXT records are written with TTL 300 for this reason.

## mock

A file-backed record store for testing – no network, no credentials. Record logic (TLSA hashing, add/delete decisions) still comes from real dnsuptools, so log output stays representative.

| key | default | description |
|---|---|---|
| `mockstore` | `/tmp/cryptdomainmgr_mockdns.json` | path of the JSON record store |

## Record types

Per domain section (`[domain:example.org]`):

| key | example | description |
|---|---|---|
| `ip4` / `ip6` | `ip4=1.2.3.4,1.2.3.5` | A/AAAA records, old values are removed on update |
| `mx` | `mx=mx1.example.org:10` | MX records with priority |
| `spf` | `spf=+mx,-ip4:0.1.2.3/24,~all` | SPF record |
| `dmarc` | `dmarc.p=quarantine dmarc.rua=mailto:...` | DMARC policy record |
| `caa` | `caa=0 issue letsencrypt.org` | CAA records |
| `srv` | `srv._tcp=server:50:10:25` | SRV records |
| `dkim.<name>` | `dkim.mydkim=auto` | publishes the public key of `[dkim:mydkim]` |
| `tlsa.<proto>.<port>` | `tlsa.tcp.443=auto:3:1:1` | TLSA records derived from the referenced certificate (`auto` = computed from the live certificate) |
| `cert` | `cert=mycert` | references `[cert:mycert]` for TLSA generation |
| `acme` | managed automatically | dns-01 challenge tokens, written/removed by the cert handler |

See [exampleconf/example_tlsa.conf](https://github.com/TheTesla/cryptdomainmgr/blob/master/exampleconf/example_tlsa.conf) for the full syntax of each type.
