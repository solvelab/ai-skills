# server_cfg.ini — field reference

INI, section-per-block. ASCII/UTF-8 without BOM; CRLF tolerated but keep LF. Comments with `;`.
Values below reflect a validated freeroam deployment (DriveZone on SRP/tatsumi_pa).

## [SERVER]

| Field | Format | Rules / pitfalls |
|---|---|---|
| `NAME` | free text | Shown in Content Manager. Avoid `;` (comment char). |
| `CARS` | ids joined by `;` | EVERY id must exist as `content/cars/<id>/`. Human + traffic models together. No spaces around `;`. |
| `TRACK` | track dir id | Must equal `content/tracks/<id>/`. NEVER a `_ptb`/beta variant mixed with stable content. |
| `CONFIG_TRACK` | layout dir id | Layout subdir of the track (`tatsumi_pa`). Empty = single-layout track. |
| `MAX_CLIENTS` | int | = number of `[CAR_N]` blocks in entry_list.ini INCLUDING `AI=Fixed` slots. Recount every time slots change. |
| `UDP_PORT` / `TCP_PORT` | int | Same value (9600). Must match compose port maps and WSL2 portproxy. |
| `HTTP_PORT` | int | 8081. `curl http://HOST:8081` = cheapest liveness probe. |
| `PASSWORD` | string | Empty = open. Never commit a real one (examples only). |
| `ADMIN_PASSWORD` | string | Required for `/admin` (the in-game dynamic-message channel). Never commit. |
| `WELCOME_MESSAGE` | file path | MUST be a path (`cfg/welcome.txt`), never inline text — validator rejects inline. |
| `REGISTER_TO_LOBBY` | 0/1 | 0 for private/LAN (server won't appear in CM lobby list; connect direct by IP). |
| `LOOP_MODE` | 0/1 | 1 = sessions loop forever (freeroam standard). |
| `SUN_ANGLE` | int | Time of day. |
| `RACE_OVER_TIME` | seconds | Grace period after session end. |

## [PRACTICE]

| Field | Rules |
|---|---|
| `NAME` | Session name shown to players. |
| `TIME` | Minutes. NEVER 0 — `TIME=0` can restart the session in a tight loop. Use 1440 for a day-long freeroam. |
| `IS_OPEN` | 1 = joinable anytime. |

Freeroam runs PRACTICE only. Adding `[QUALIFY]`/`[RACE]` changes the session cycle — don't,
unless you mean to.

## [DYNAMIC_TRACK]

`SESSION_START` (grip % at start), `RANDOMNESS`, `SESSION_TRANSFER`, `LAP_GAIN`. Baseline:
90 / 0 / 80 / 1.

## [WEATHER_0]

`GRAPHICS` must be a weather id the CLIENT has (`3_clear` is safe stock).
`BASE_TEMPERATURE_AMBIENT/ROAD`, `VARIATION_*`, `WIND_*` are plain ints. Multiple `[WEATHER_N]`
blocks = random rotation; one block = deterministic.

## What lives elsewhere

- AI traffic, CSP requirements, plugins, log level → `extra_cfg.yml` (AssettoServer-only file).
- Per-slot car/skin/AI assignment → `entry_list.ini` (see entry-list-skeleton.md).
- The stock `acServer` ignores `extra_cfg.yml`; AssettoServer reads all three. Keep the trio
  consistent — the validator (`validate-config.sh`) cross-checks them before boot.
