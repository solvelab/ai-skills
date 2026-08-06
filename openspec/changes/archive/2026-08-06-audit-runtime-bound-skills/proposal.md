# Change: Audit the skills whose runtime this environment does not have

## Why

Five skills had only ever received mechanical validation, every audit stopping at the same excuse:
`assettoserver-ops`, `assettoserver-plugin` and `assettoserver-csp-lua` need an Assetto Corsa server,
`fivem-lua` needs FXServer, `openspec-drivezone` needs the DriveZone repos. None of that is available
here.

The excuse was partly wrong. Three lenses do not need the runtime: reading the doctrine, applying the
five defect classes `bug-hunter` gained in #37, and probing the parts of the claim that are public.
Two real defects came out.

**1. `assettoserver-plugin` prescribes the exact TFM its own rule forbids.** Its version-pinning
section says to inherit the target framework from upstream and gives
`<TargetFramework Condition="'$(TargetFramework)' == ''">net9.0</TargetFramework>` as the fallback.
Ninety lines later its forbidden-constructs table bans `System.Threading.Lock` because the "type
[is] missing in the host runtime".

Both cannot be true. `System.Threading.Lock` ships in **.NET 9**, so on a `net9.0` host it exists.
Probed against upstream: `AssettoServer/AssettoServer.csproj` at tag **v0.0.54** targets **`net8.0`**.

So the ban is correct and **the fallback is the bug** — and it is the worst possible kind, because a
fallback applies precisely when detection failed. Compiling a plugin for `net9.0` against a `net8.0`
host is the "undefined behavior at load time" that same section exists to prevent, and it silently
makes `System.Threading.Lock` compile so the runtime can fail on it later.

**2. `fivem-lua` rejects forged input silently.** Its trust-boundary section — "the most important
rule" — validates type, presence and range and then `return`s. The word *log* appears nowhere in the
skill. A server under attack therefore looks exactly like a quiet one, and the same section's
instruction to "rate-limit it" has no counter to rate-limit on. This is the **Observable degradation**
class added to `bug-hunter` in #37, applied to a skill that had never been given that lens.

## What Changes

- `assettoserver-plugin` → 1.3.0:
  - TFM fallback corrected to `net8.0`, with the probed evidence (upstream v0.0.54) recorded inline,
    and a note that a fallback default is a trap because it applies exactly when detection failed.
  - The `System.Threading.Lock` row states *why* it is absent (a .NET 9 type on a net8.0 host) and is
    explicitly **version-scoped**: when the pin moves to a .NET 9+ runtime the ban must be lifted, and
    the Cecil assert scoped to the detected TFM rather than asserted unconditionally.
- `fivem-lua` → 1.3.0: a rejection-counter rule at the trust boundary — count and log every rejected
  event with its `source`, rate-limit on the counter, escalate a player past the threshold instead of
  validating them one message at a time forever. The Lua added was syntax-checked with `luac -p`.

## Deliberately unchanged

`assettoserver-ops` and `assettoserver-csp-lua` were read in full and scanned with the same lenses.
Both already state their enforcement layer densely (24 and 38 references to a script, gate or CI
check), and none of the five defect classes applies cleanly to what they cover. **No edit was
manufactured for them.** `openspec-drivezone` states its two-layered enforcement and the CLI's real
limitation correctly, which an earlier change already corrected.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — a skill that cannot be exercised in the working environment
  SHALL still be audited by reading, by the adversarial defect classes, and by probing the public part
  of its claims; "no runtime" is not a reason to leave it unaudited.

## Impact

- `skills/assettoserver-plugin/SKILL.md`, `skills/fivem-lua/SKILL.md`, regenerated wrappers.
- A plugin built by following the corrected skill targets the framework its host actually runs.
- A FiveM resource built by following the corrected skill can tell that it is being attacked.
