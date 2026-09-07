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
- **StateBag races**: concurrent writers to the same networked state don't corrupt it — drive it with
  a burst of writers, not a pair.

## Generating and scoring here: what the ecosystem actually offers

Probed on 2026-09-07 with `luarocks 3.13.0`, because the two conditional layers of the rite are
worth nothing if the reader has to discover on their own that the tools do not exist.

**Generate — no.** The ecosystem's property-based library is `lua-quickcheck`, and LuaRocks answers
directly:

```bash
luarocks install lua-quickcheck --check-lua-versions
# lua-quickcheck supports only Lua 5.1 and Lua 5.2 but not Lua 5.5.
```

CfxLua is 5.4-based, so the library does not reach the runtime this track targets. Re-run that one
line before believing this paragraph — it is a fact with a date, and a rock supporting 5.4 could
appear.

**Score — nothing to reach.** There is no mutation-testing rock. Three exact-name searches returned a
header and an empty result set:

```bash
luarocks search mutmut ; luarocks search mutation-testing ; luarocks search luamutant
```

**So what this track does instead.** Enumeration is the whole rite here, which makes it weaker than
the Python track and worth saying out loud: nothing will generate the case you did not think of, and
nothing will tell you the suite is thin. The boundary witnesses the scoring layer would have found
have to be written by hand — for every limit the code enforces, a case on each side and one **at the
value**, because a suite that proves a clamp fires and never where it sits survives the clamp being
moved.

The runner is `busted`, and installing it is two steps, not one — the second is the one people lose
an afternoon to:

```bash
luarocks --local install busted          # busted 2.3.0-1 is now installed
eval "$(luarocks path --bin)"            # WITHOUT this: `command not found: busted`
busted --verbose
```

`--local` puts the binary in `~/.luarocks/bin`, which is not on `PATH`. Probed on 2026-09-07 against
`luarocks 3.13.0` and Lua 5.5.0, driving a five-case spec over a pure clamp module: `5 successes / 0
failures`, and moving the clamp's own constant from 100 to 101 turned the case that asserts the value
red — which is the witness this section exists to demand. In the same run, `>` widened to `>=`
survived every case, and that one is correct: for a clamp that returns the maximum either way the
mutant is equivalent, which is why survivors are read by class and never as a percentage.

## Exit criteria

Everything unit-testable is covered off-game and green; what can't be unit-tested has a **documented
in-game smoke** covering the adversarial path (not just the happy one), executed and checked off.
