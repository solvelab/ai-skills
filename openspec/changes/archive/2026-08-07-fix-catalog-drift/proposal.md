## Why

Five claims in this repository are wrong, each because a number or a list was written by hand and
then drifted from the thing it describes. They were found by running the derivation instead of
trusting the sentence.

| Claim | Where | Re-derived |
|---|---|---|
| "FULL bundle (all 27 skills)" | `.claude-plugin/marketplace.json` | `ls skills \| wc -l` → **33** |
| "whoever really wants all 30" | `README.md:55` | **33** |
| "dumping all 30 skills into every project" | `README.md:82` | **33** |
| "runs six checks" | `README.md:668` | the script's own docstring declares **C1..C8** — eight, and the sentence lists only six |
| category set `{backend, testing, fivem, game, devops, docs, git, process}` | `openspec/specs/skills-authoring/spec.md:28` | `.github/workflows/ci.yml:54` enforces **11**: it adds `nui`, `frontend`, `tooling` |

The last one is the most damaging: the document a contributor reads to learn the rule disagrees with
the gate that applies it. A contributor following the spec would believe three categories already in
use are invalid.

This is the same defect class the anti-guessing work targets — a confident sentence nobody
re-derived — which makes fixing it the cheapest available demonstration that the doctrine is worth
anything.

## What Changes

- Correct the two published skill counts and the bundle description count.
- Correct the validator description: eight checks, with the two that were missing from the prose
  (`no orphan wrapper skills`, `no meta sections in SKILL.md`) named.
- Bring the `skills-authoring` controlled category set into agreement with the CI job that enforces
  it, as a `MODIFIED` requirement.
- Where a number is now written, name the command that produces it, so the next editor can re-derive
  rather than re-copy.

## Capabilities

### Modified Capabilities

- `skills-authoring`: the controlled set of `metadata.category` values is restated to match the gate
  that enforces it, adding `nui`, `frontend` and `tooling`.

### New Capabilities

_None._

## Impact

- `.claude-plugin/marketplace.json` — bundle description count.
- `README.md` — two counts and the validator description.
- `openspec/specs/skills-authoring/spec.md` — via the change's spec delta.
- No skill file, no script and no generated tree is touched, so nothing regenerates and no consumer
  behaviour changes. This is a documentation-truth change only.
