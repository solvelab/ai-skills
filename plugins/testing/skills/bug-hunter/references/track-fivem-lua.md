# Track — FiveM / Lua

FiveM has no headless runtime, so split the work between off-game unit tests and a documented in-game
smoke.

## Scenarios

- **Pure modules (busted/plain Lua)**: parsing, config validation, payload shaping, clamping, math —
  test these off-game. Most logic bugs live here and are testable.
- **Fallback under failure**: simulate backend/Consul down (timeout, 5xx, partial payload) → safe
  default, no crash, no silent stale state. (Expected behavior: `fivem-fallback`.)
- **Event injection**: for each server `RegisterNetEvent` handler — send forged/out-of-range args, a
  `targetServerId` equal to self / nonexistent / not-permitted; confirm the actor is taken from
  `source`, not client args (rule: `fivem-lua`); confirm rate-limiting on relay-to-other-player.
- **NUI callbacks**: malformed `event`/`payload` (missing fields, wrong type) must not nil-deref or
  trigger unintended state.
- **Lifecycle**: disconnect/close mid-flow (ESC included) releases locks/focus and cleans per-player
  state; resource restart doesn't leave orphaned globals.
- **StateBag races**: concurrent writers to the same networked state don't corrupt it.

## Exit criteria

Everything unit-testable is covered off-game and green; what can't be unit-tested has a **documented
in-game smoke** covering the adversarial path (not just the happy one), executed and checked off.
