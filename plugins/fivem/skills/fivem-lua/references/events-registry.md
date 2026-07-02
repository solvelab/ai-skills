# Reference — central event registry + declared boot order (production-extracted)

Pattern from a ~65-resource production server: one catalog resource owns every cross-resource event
name and the post-spawn boot order. Kills the two classic multi-resource failure modes — event-name
typos that fail silently, and resources that assume another one already booted.

## Event catalog

One shared module exposes constants; NOTHING hardcodes event strings:

```lua
-- events-catalog/shared/Events.lua
Events = {}

Events.serverEvents = {   -- client -> server
  MYRES_CONFIG_FETCH = "my-resource:config:fetch",
  MYRES_ACTION       = "my-resource:action",
}

Events.clientEvents = {   -- server -> client (+ client-local)
  MYRES_CONFIG = "my-resource:config",
  MYRES_STATE  = "my-resource:state",
}

Events.nativeEvents = {   -- engine events (playerDropped, onResourceStart, ...)
  PLAYER_DROPPED = "playerDropped",
}

function GetEventsInstance()
  return Events
end
```

Consumers:

```lua
local Events = exports["events-catalog"]:GetEventsInstance()
RegisterNetEvent(Events.serverEvents.MYRES_ACTION, function(payload) ... end)
TriggerClientEvent(Events.clientEvents.MYRES_STATE, src, data)
```

**Catalog vs raw decision tree**: catalog every event that crosses a resource boundary or a
network boundary; keep raw only what is purely internal to one file. Drift detector (CI/grep):

```bash
grep -rn 'RegisterNetEvent("' scripts/ --include='*.lua' | grep -v events-catalog
```

**Anti-cheat variant (optional)**: encrypt `serverEvents`/`clientEvents` values at boot with a
per-session XOR key distributed via a replicated convar — event names in memory dumps become
useless across sessions. Trade-off: any change to the catalog then requires a FULL server restart
(never an isolated resource restart), because clients and server must re-derive the same key.

## Declared boot order

A second shared table declares the ordered post-spawn boot layers; the spawn orchestrator iterates
it firing `<resource>:start` — no resource guesses when its dependencies are up:

```lua
Envs.resources = {
  primary = { "core", "rest-bridge" },       -- pre-spawn infra
  secondary = {                              -- post-spawn, dependency-ordered layers
    -- layer 1: catalogs/infra consumed by everyone
    "text-ui", "blip-manager",
    -- layer 2: character systems
    "inventory", "character-status",
    -- layer 3: vehicles (key before hud; energy/condition after)
    "vehicle-key", "vehicle-hud", "vehicle-energy", "vehicle-condition",
    -- layer 4: jobs (consume everything above)
    "job-center", "job-delivery",
  },
}
```

New resource = one ordered entry here + the server cfg `ensure` + the dev ensure-script (see the
"New resource checklist" in the skill). A resource missing from the boot list fails LOUDLY at the
orchestrator instead of silently never starting its gameplay loop.
