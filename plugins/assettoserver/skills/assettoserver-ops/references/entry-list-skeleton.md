# entry_list.ini — skeleton and indexing rules

## Hard rules

- Blocks MUST be `[CAR_0]`, `[CAR_1]`, ... contiguous, zero-based, no gaps, no duplicates.
  A gap silently shifts slot resolution and breaks joins.
- Block count == `MAX_CLIENTS` in server_cfg.ini (AI slots INCLUDED).
- Every `MODEL` must appear in `CARS` (server_cfg.ini) and exist on disk
  (`content/cars/<model>/`); every `SKIN` must exist as `content/cars/<model>/skins/<skin>/`.
- Human pickup slots come FIRST (CAR_0..CAR_k), traffic slots after — players can then never
  spawn a traffic vehicle.
- Traffic slots MUST carry `AI=Fixed`. A slot without `AI=` is a HUMAN slot: forgetting the
  flag on a traffic block silently turns it into a joinable traffic car.
- `GUID=` empty on open slots; set a SteamID64 to reserve a slot for one player.

## Skeleton (2 human + N traffic, the validated shape)

```ini
[CAR_0]
MODEL=aegis_mitsubishi_lancer_evolution_v_gsr
SKIN=<existing skin dir>
DRIVERNAME=DriveZone Local Driver 1
TEAM=
GUID=
SPECTATOR_MODE=0
BALLAST=0
RESTRICTOR=0

[CAR_1]
MODEL=aegis_mitsubishi_lancer_evolution_v_gsr
SKIN=<existing skin dir>
DRIVERNAME=DriveZone Local Driver 2
TEAM=
GUID=
SPECTATOR_MODE=0
BALLAST=0
RESTRICTOR=0

[CAR_2]
MODEL=traffic_toyota_prius
SKIN=<existing skin dir>
DRIVERNAME=DriveZone Traffic 01
TEAM=DriveZone Urban Traffic
GUID=
AI=Fixed
SPECTATOR_MODE=0
BALLAST=0
RESTRICTOR=0

; ...repeat one block per traffic car, incrementing CAR_N and Traffic NN.
; Last block index must be MAX_CLIENTS - 1.
```

## Change checklist (any slot edit)

1. Re-number: indices contiguous from 0.
2. Recount: blocks == `MAX_CLIENTS`.
3. Cross-check: every MODEL in `CARS`; every MODEL/SKIN dir exists on disk.
4. `AI=Fixed` present on every traffic block, absent on human blocks.
5. Run `validate-config.sh` (it enforces 2–4 mechanically).
