# Architecture

## Phase model

Every run executes one phase over all modules. The phases implement the zero-downtime strategy:

| phase | cert | dkim | domain | service |
|---|---|---|---|---|
| `prepare` | issue certificate via ACME, publish new TLSA/DKIM records | generate key pair, publish public key | publish records that depend on cert/dkim results | – (marked done) |
| `rollover` | deploy certificate to destinations | deploy key to `keylocation` | – | render service configs, reload services |
| `cleanup` | remove obsolete files | – | remove obsolete records | – |
| `update` | – | – | publish static records (A/AAAA, MX, CAA, ...) | – |

`--next` picks the phase following the last completed one (tracked in the state file), so a cron setup can simply run `cryptdomainmgr --next` repeatedly.

## Handler dispatch

Each module (`cert`, `dkim`, `domain`, `dhparam`, `service`) has:

* `main.py` – phase entry, loops over the config sections of its module
* `confighandler.py` – interprets raw ini sections into handler-ready dicts (applies `DEFAULT` sections and handler defaults)
* `handler<name>.py` – one file per handler, selected via the `handler=<name>[/<ca>]` config key

Handlers are resolved by dynamic import (`__import__('cryptdomainmgr.modules.<mod>.handler' + name)`). Adding a handler is a new file with `prepare`/`rollover`/`cleanup` (+ `update` for domain) and a `defaultConfig` dict – no registration anywhere.

### Fallbacks

When a configured handler does not exist (e.g. configurations for handlers removed from the project), the cert module falls back to the acme handler with a warning; legacy config values are translated at config interpretation time. New modules can follow the same two-layer pattern: config-time translation (unit-testable without servers) plus an ImportError fallback at dispatch.

## State handling

The state machine (`cdmstatehandler.py`) tracks per-section operation states (`uninitialized → waiting → running → done`) recursively. Cross-module dependencies are expressed via `depends`/`requires` in the config and checked with `isReady()` – e.g. the opendkim service handler waits until its dkim section is done before writing the KeyTable.

The state file (`<statedir>/state.json`) persists results (certificate file paths, DKIM selectors, key hashes) between phases.

## Run summary

Every run ends with a summary log line: on success a compact overview (phase, duration, opstate per module/section). On failure the summary additionally contains the full exception traceback and the complete state tree including section results (certificate paths, selectors) – everything needed to diagnose the failure without re-running in debug mode.

## Module responsibilities

The layering is strict:

* **dkim handlers** only generate and deploy keys + selectors – they know nothing about mail servers
* **service handlers** own everything service-specific (config formats, reloads) and consume dkim/cert results
* **domain handlers** own all DNS writes; the acme handler publishes challenge records by calling the configured domain handler in-process (no subprocess, no credentials on the command line)
