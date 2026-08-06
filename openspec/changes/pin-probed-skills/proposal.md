# Change: Pin the skills whose external surface was actually probed, and widen the pin detector

## Why

`Versioned external APIs are pinned` requires a skill targeting a versioned external surface to state
what it was verified against. The validator's C5 check enforces it — but only for skills carrying **40+
lines of fenced code**. A skill that makes the same claims in prose escapes entirely.

`fivem-nui-react` is the clean example: **zero** fenced lines, and four concrete assertions about a
Vite build for CEF. All four were probed against `vite 8.2.0` + `terser 5.49.2` and **all four hold**:

| claim | result |
|---|---|
| `base: './'` — absolute paths 404 in CEF | emits `./assets/index.js`, `./assets/index.css` |
| flat, hash-less `entryFileNames` so `dist/assets/*` matches | `assets/index.js`, `assets/index.css` |
| `drop_console: true` | 0 occurrences of `console.log` in the bundle |
| `dist/index.html` + `dist/assets/*` matches the fxmanifest | both present, nothing else |

Correct doctrine, unverifiable by the reader. That is what a pin fixes.

The pin **detector** was also wrong in both directions:

- **False negatives** — it missed `runtime 0.0.54 ↔ upstream tag v0.0.54` (`assettoserver-plugin`) and
  `Probed on CLI 1.6.0` (`openspec`), reporting two correctly-pinned skills as unpinned.
- **Blind spot** — the 40-fenced-line trigger, described above.

## What Changes

- `scripts/validate-skills.py`: PIN regex widened to recognise `Probed on`, and
  `runtime|tag|CLI|preset <version>` forms. The 40-line trigger stays; its limit is now stated in the
  check's own docstring rather than implied.
- Pins added to the three skills whose surface was probed tonight:
  - `backlog` → 1.0.2 and `execute-backlog` → 1.2.1: `gh 2.92.0`, the client every recipe was probed
    against (28 subcommand/flag claims across the process skills, all clean).
  - `fivem-nui-react` → 1.0.1: `vite 8.2.0` + `terser 5.49.2`, with what each build rule produced.
- `react-api-client` → 1.1.1: one `ts` block in `references/api-client.md` does not parse — top-level
  `await` and shorthand properties with nothing in scope. Marked as an excerpt, matching the
  convention used across `r3f-*`. The other three blocks parse.

## Deliberately not done

Four skills target a versioned surface and remain unpinned because **the surface was not probed**:
`assettoserver-csp-lua` (CSP Lua API), `fivem-lua` and `fivem-fallback` (CitizenFX natives), and
`react-api-client` (axios/zod — its reference blocks carry no imports, so a compile probe would only
measure the missing imports). Writing a pin for a version nobody checked would be the exact failure
this requirement exists to prevent. They are recorded here as a known gap.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Authoring rules are machine-enforced** — a mechanical check that only
  covers part of its rule SHALL state the uncovered part, so a passing run is not read as full
  coverage.

## Impact

- `scripts/validate-skills.py`; `skills/{backlog,execute-backlog,fivem-nui-react}/SKILL.md`;
  `skills/react-api-client/references/api-client.md`; regenerated wrappers.
- No README change: no skill added, removed or repurposed.
