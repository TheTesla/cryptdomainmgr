# Testing

The test suite runs **offline by default** – no INWX access, no LetsEncrypt, no rspamd required.

```bash
python -m unittest discover
```

## Test layers

| layer | what | external services |
|---|---|---|
| unit tests | config interpretation, state machine, phase logic | none |
| pebble e2e (`test/modules/cert/test_cert_pebble.py`) | full ACME flow for the acme handler incl. TLSA hash assertions, run against the local [pebble](https://github.com/letsencrypt/pebble) ACME server | none (pebble binary needed) |
| opendkim/rspamd-conf e2e | dkim key generation + service config rendering, with the mock DNS handler | none |
| live integration tests | real INWX API and LetsEncrypt staging | INWX + LetsEncrypt |

## Skip gates

* live INWX tests skip unless a credentials file `test_inwxcreds.conf` exists in the repo root (never committed)
* LetsEncrypt staging tests additionally require `CDM_LIVE_STAGING=1` – they touch the real staging API and are run sparingly, only as a final confirmation:

```bash
CDM_LIVE_STAGING=1 python -m unittest test.modules.complextests.test_certtlsa
```

* rspamd handler tests need a real rspamd + sudo and fail on machines without them (they skip in CI) – check which class a failure belongs to before debugging

## Pebble end-to-end

The pebble binary is looked up via `PEBBLE_BIN`, `PATH`, then `~/.local/bin/pebble`. Build it with:

```bash
go install github.com/letsencrypt/pebble/v2/cmd/pebble@latest
```

!!! warning "Module path"
    The unversioned go module path pulls the dead pebble v1.0.1 from 2019 – the `v2` path is the active series.

The pebble fixture starts a per-test-run server on a free port with a self-signed WFE certificate (`PEBBLE_VA_ALWAYS_VALID=1`, challenge validation is answered via the mock DNS handler), so the full prepare → rollover → cleanup flow runs without internet.

## CI

GitHub Actions (`.github/workflows/tests.yml`): unittest matrix (3.10–3.13) and the pebble e2e job on every push. The `live-staging` job runs only on manual `workflow_dispatch` and only after the offline jobs passed.
