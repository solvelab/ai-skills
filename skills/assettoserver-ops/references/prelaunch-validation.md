# Pre-launch validation checklist

Run through this BEFORE `docker compose up` / before a session with players. Every step is a
script, not a judgment call. Scripts live in `server/scripts/` and run via
`docker compose run --rm assetto-server /assetto/scripts/<name>.sh`.

## 1. Static config gate — `validate-config.sh`

Blocks boot (start-server.sh calls it) when any of these fail:

- [ ] `server_cfg.ini`, `entry_list.ini`, `extra_cfg.yml` exist
- [ ] Required keys present: `NAME`, `CARS`, `TRACK`, `MAX_CLIENTS`, `UDP_PORT`, `TCP_PORT`, `HTTP_PORT`
- [ ] `[CAR_0]` exists; its `MODEL` == first id in `CARS`; its `SKIN` dir exists
- [ ] Every `MODEL`/`SKIN` of every `[CAR_N]` exists under `content/cars/`
- [ ] `TRACK` dir and `CONFIG_TRACK` layout dir exist under `content/tracks/`
- [ ] `MAX_CLIENTS` ≤ number of `[CAR_N]` blocks
- [ ] `WELCOME_MESSAGE` points to an existing FILE (inline text rejected)
- [ ] `[PRACTICE] TIME` ≠ 0 (warning — restart-loop hazard)
- [ ] AI gate: if `EnableAi: true` → at least one `AI=Auto|Fixed` slot AND
      `tracks/<track>/ai/fast_lane.ai|.aip` present; otherwise FAIL with
      "keep traffic disabled"

## 2. Content ↔ config agreement

- [ ] `inspect-content.sh` — configs vs mounted content
- [ ] `audit-traffic-support.sh <layout>` — prints a Decision line
      (`traffic may be testable` / `keep traffic disabled`); required before ANY
      traffic enablement or density change
- [ ] No `_ptb`/beta variant anywhere (track dir, lane file, client pack)
- [ ] `print-client-requirements.sh` output matches what players were told to install

## 3. Runtime smoke

- [ ] `smoke-server.sh` — boots the real runtime for N seconds, fails if it dies
- [ ] Plugin enabled? `prove-drivezone-plugin-load.sh` first (loads plugin against a
      TEMPORARY config, confirms via log, leaves real config untouched)
- [ ] Plugin DLL updated? `sync-drivezone-plugin.sh` only — it refuses without a
      `plugin-rite-status.json` newer than the DLL

## 4. Stack + network (session day)

- [ ] `drivezone-up.sh` → `drivezone-healthcheck.sh` (backend :5001/health, server :8081,
      containers Up) → `drivezone-status.sh`
- [ ] `curl http://<HOST>:8081` from a machine on the LAN
- [ ] WSL2: portproxy re-pointed at the CURRENT WSL IP (`wsl hostname -I` — it changes on
      reboot); firewall rules for 9600/tcp, 9600/udp, 8081/tcp
- [ ] `check-runtime-logs.sh` clean of `warning|error|exception|crash`
- [ ] Collector (if used): `--profile collector` up, `check-collector-state.sh` shows a
      fresh `state.json`

## 5. Before any risky change (not just launch)

- [ ] Snapshot configs: `server/cfg/backups/<label>-<timestamp>/`
- [ ] OpenSpec rite for relevant changes: `openspec validate <id> --strict`,
      `bash -n server/scripts/*.sh collector/*.sh`, `docker compose config`, `docker compose build`
- [ ] Rollback plan is a copy-back (backups/) or `EnablePlugins: []` — never hand-editing
      the runtime volume
