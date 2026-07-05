# Checksum / content / connection troubleshooting

Distilled from a production runbook. Before diagnosing anything, restate the pinned baseline the
server runs (pack version, track id, layout id, human car id, skin ids, CSP required) and confirm
the player installed exactly that — most "server bugs" are content drift on the client.

## Symptom → cause → fix

| Symptom | Likely cause | Player fix | Operator check |
|---|---|---|---|
| `checksum mismatch` | different pack version; stable/`_ptb` mix; different car/skin/traffic pack; files in the wrong folder | reinstall the exact operator pack; confirm track id has no `_ptb` suffix; rescan in Content Manager | `print-client-requirements.sh`, `check-runtime-logs.sh`, `inspect-content.sh` |
| `track version mismatch` | player has another pack version or the `_ptb` variant; Content Manager points at another game install | remove the wrong variant, keep only the pinned pack; validate `content/tracks/<track>/<layout>/` | same as above |
| "track missing" for the layout | track installed but layout folder absent | validate `<layout>/`, `ui/<layout>/ui_track.json`, `models_<layout>.ini` | `validate-config.sh` |
| AI spline error / traffic won't start | lane file from a different variant (the classic: `_ptb` spline on the stable track) | — | validate `tracks/<track>/ai/fast_lane.aip` matches the track variant; `audit-traffic-support.sh <layout>` |
| `Car "<id>" is missing.` | car not installed or folder nested one level too deep | install `content/cars/<id>/`; check for nesting | `validate-config.sh` |
| join fails / slot doesn't resolve | missing skin folder | install the exact `skins/<skin_id>/` dirs | `validate-config.sh`, `diagnose-server.sh` |
| connects but visuals/traffic wrong or missing | CSP missing/incompatible on the client | install/upgrade CSP compatible with the shared content; restart Content Manager | confirm `CSP.Enabled` and required version in `extra_cfg.yml` |
| server absent from Content Manager list | lobby disabled (`REGISTER_TO_LOBBY=0`), CM filter, firewall | connect direct via `HOST:9600`; test `curl http://HOST:8081` | confirm 9600/tcp, 9600/udp, 8081/tcp are published (WSL2: portproxy + firewall) |
| connect timeout | network/firewall, wrong port, server down | test `:8081` over HTTP; confirm host/port | `drivezone-healthcheck.sh`, `check-runtime-logs.sh` |
| kicked/disconnected mid-session | content divergence, network, session reset | — | `check-runtime-logs.sh`, `diagnose-server.sh` |
| player sees no AI traffic | client lacks traffic cars; CSP incompatible; traffic disabled server-side | install the urban-cars pack; confirm CSP | confirm `EnableAi: true` in the live config; layout unchanged; AI activity in logs |

## Log lines to grep (server runtime logs)

```
attempting to connect
has connected
failed checksum
checksum mismatch
AI Slot
reached spline
warning | error | exception | crash
```

## The `_ptb` rule

Any reference to `<track>_ptb` (or another beta variant) in logs, configs, or a player's install is
treated as wrong content — remove the mix, return to the pinned stable pack, keep the pinned
layout. Do not "make it work" with mixed variants; the failure modes are non-obvious (splines,
checksums, traffic) and come back later.

## What a player report must include

Exact Content Manager error text; host/port used; confirmation of pack version, track, layout, car
and skins; whether the variant is `_ptb`-free; whether traffic appears; a screenshot when possible.
Publish this list to players — it turns "can't join" reports into one-round-trip diagnoses.
