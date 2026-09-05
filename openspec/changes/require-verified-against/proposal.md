# Change: Require the literal `Verified against` block, probed, on every skill

## Why

`skills-authoring` (*Versioned external APIs are pinned*) asks a skill about a versioned tool to say
which version its claims were checked against. Measured on 2026-09-05 with
`grep -L 'Verified against\|does not depend on a tool version' skills/*/SKILL.md`: **20 of 35** skills
carry neither, among them skills that describe versioned surfaces (`assettoserver-*`, `fivem-*`,
`react-api-client`, `backend-resilience`, `api-resilience-testing`). Some of those *do* carry a
version somewhere — `openspec` says "Probed on CLI 1.6.0", `assettoserver-plugin` says
"runtime 0.0.54 ↔ upstream tag v0.0.54" — but a reader cannot tell a pin from a mention, and neither
can the validator: `check_pin` (C5) accepts any `<word> <digits>.<digits>` and only looks at skills
with 40+ fenced lines, so a prose-only skill and a loosely worded one both pass.

The issue (#131) also names the failure this change must not commit: writing `Verified against CSP
0.2.x` without running CSP is inventing a pin, worse than none. The re-analysis found more probe
surface on this machine than the issue assumed — `~/works/AssettoServer` at tag `v0.0.55-pre25`, the
DriveZone server image (`AssettoServer 0.0.55+51d8d8a6e0`), docker images for Lua 5.4.8, Helm v4.2.3
and the .NET 9 SDK, the live status line of Claude Code 2.1.261, gh 2.96.0, openspec 1.6.0 — but not
the CSP client, not an FXServer build, and not the project `react-api-client` was extracted from.
What can be probed is probed; what cannot is written down inside the block as not probed.

## What Changes

- **Two literal declarations**, one of which every `SKILL.md` carries:
  - `> **Verified against**: <tool> <version> · … — <what was run>. Probed on <YYYY-MM-DD>.` The
    block also names the part of the skill that was **not** probed, when there is one.
  - `> **Not version-bound**: this skill does not depend on a tool version — <reason>.`
- **20 skills** get one of the two, each with a patch bump:
  - Probed here and pinned: `assettoserver-ops`, `assettoserver-plugin`, `assettoserver-csp-lua`
    (API names against the public `acc-lua-sdk` stubs; in-game behaviour stays unprobed and says so),
    `fivem-lua`, `fivem-fallback` (Lua 5.4.8 syntax + natives against `citizenfx/natives`; no
    FXServer build, said so), `react-api-client` (blocks typechecked against pinned axios/zod/tsc),
    `backend-resilience`, `log-event-collector`, `api-resilience-testing` (re-measured on the pinned
    FastAPI/pydantic), `claude-statusline`, `code-locale`, `openspec`, `openspec-drivezone`,
    `backlog`, `execute-backlog`, `conventional-commit` (this repo's release tooling), `svg-animation`
    (Chrome for Testing 151.0.7922.34, the browser `references/platform.md` was measured on).
  - Declared not version-bound: `helm-migration` (prescribes the shape of a private chart's values
    file and already defers to the local template; it prescribes no `helm`/`kubectl` command),
    `bug-hunter`, `documentation`.
- **`check_pin` (C5) becomes catalog-wide and literal**: every `SKILL.md` must carry one of the two
  phrases; a loose version mention no longer counts; a skill with 40+ fenced lines against a versioned
  API that carries only the declaration is reported unless it defers to a local source of truth. The
  40-fenced-line KNOWN LIMIT is removed with the trigger. The selftest gains the mutations that prove
  each rule fires (pin removed from a code-heavy skill; pin reworded to a loose mention; declaration on
  a code-heavy API skill).
- README paragraph on the validator updated (C5 wording, selftest count).

## Deliberately not done

- The **date** inside the block is required by this issue for the 20 blocks written here and is not
  enforced by C5: the 15 blocks that already exist carry no date and were probed on other days
  (their archived changes carry the date). Enforcing it means backfilling 15 skills — a follow-up.
- `assettoserver-plugin` keeps its `v0.0.54` / `net8.0` doctrine. The DriveZone runtime measured today
  is `0.0.55+51d8d8a6e0`, built from a tree whose `AssettoServer.csproj` targets `net9.0`; the pin
  block **discloses** that contradiction (the spec's "known breaking change" scenario) and a follow-up
  issue re-derives the TFM and the `System.Threading.Lock` ban for that runtime. Rewriting the
  doctrine is not this item's scope.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Versioned external APIs are pinned** — every skill carries one of two
  literal declarations; a loose version mention is not a pin; a code-heavy skill against a versioned
  API cannot exit by declaration; a partial probe names what was not probed.

## Impact

- `skills/<20 names>/SKILL.md` (block + patch bump), regenerated wrappers under `claude/ codex/
  cursor/ copilot/ plugins/`.
- `scripts/validate-skills.py` (C5), `scripts/selftest-validate-skills.py` (new mutations),
  `README.md` (validator paragraph).
- No skill added, removed or repurposed; catalog composition unchanged.
