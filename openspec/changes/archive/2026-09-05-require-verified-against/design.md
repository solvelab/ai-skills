## Context

`check_pin` in `scripts/validate-skills.py:254-266` (read 2026-09-05, HEAD 7709622) fires only when a
skill carries 40+ fenced lines, matches `API_HINT`, matches none of the loose `PIN` forms and does not
defer to a local source of truth. Its docstring states the 40-line KNOWN LIMIT. The result measured
today: 20 of 35 skills carry no `Verified against` block and C5 reports 0 findings.

The 15 blocks that exist share one shape — a blockquote opening with `**Verified against**:` and
listing `tool version` pairs followed by what was run (`skills/r3f-*/SKILL.md:18-22`,
`skills/observability/SKILL.md:22-25`, `skills/k8s-tune-resources/SKILL.md:23-26`,
`skills/verify-before-claiming/SKILL.md:213-216`). `python-rest-api` carries the phrase in plain
prose (`SKILL.md:183`). Both are literal `Verified against`.

## Goals / Non-Goals

**Goals:**
- A reader opening any `SKILL.md` finds, near the top, either what it was probed against and when, or
  the statement that nothing in it is version-bound and why.
- The validator reads the same two literals the reader does, on every skill.
- Every pin written by this change is backed by a command run on 2026-09-05 whose output is recorded
  in `tasks.md`; the unprobed part of a skill is named inside its block.

**Non-Goals:**
- Enforcing a date inside the block (follow-up; needs a 15-skill backfill).
- Re-deriving `assettoserver-plugin`'s TFM doctrine for the `0.0.55` runtime (follow-up issue).
- Running CSP in-game, an FXServer build, or the source project of `react-api-client`: not on this
  machine; the blocks say so instead of guessing.

## Decisions

1. **Two literal phrases, catalog-wide.** `Verified against` (case-sensitive) or
   `does not depend on a tool version`. Alternative considered: keep C5 scoped to code-heavy skills
   and accept loose forms — rejected, it is the state that let 20 skills through and the reader cannot
   distinguish "Probed on CLI 1.6.0" (a pin) from "needs CSP >= 0.1.78" (a mention).
2. **Declaration is an exit only for prose skills.** A skill with 40+ fenced lines that matches
   `API_HINT` and declares itself not version-bound is reported unless it also carries the existing
   `defers` phrase (`read the local copy first` / `source of truth, not this skill`). Rationale: the
   declaration exists for process skills; a code-heavy API skill using it is the false-negative the
   issue asks to close. `helm-migration` passes through the `defers` phrase it already carries.
3. **Partial probes stay inside `Verified against`.** No third literal. The block names tools probed
   and, in the same block, what was not (`Not probed: the in-game rendering rules; they were
   observed on the DriveZone server and carry no CSP build number here`). Alternative: a third
   literal `Unverified` — rejected because it gives a skill a way to declare nothing was checked and
   still pass, and because the criterion's grep names two forms.
4. **Patch bump per skill.** The block changes what the reader can rely on, not what the skill does.
   Precedent: `2026-08-06-pin-probed-skills` bumped 1.0.1/1.0.2/1.2.1.
5. **Existing loose pins stay as prose; the block is added.** `openspec`'s "Probed on CLI 1.6.0"
   sentences carry behaviour details worth keeping; the block above them is what C5 reads.
6. **Selftest mutations target the new rules, not the old trigger.** The current C5 mutation appends
   45 `tsx` lines to `react-api-client`, which will carry a block after this change and would stop
   firing. Replaced by: (a) strip the block from a code-heavy skill, (b) reword a block to a loose
   mention, (c) replace a code-heavy API skill's block with the declaration.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| A pin names only what was run; an unprobed claim is written as a gap | `verify-before-claiming` | already canonical — blocks link to it, none restates the ladder |
| The two literal declarations and what each owes | `openspec/specs/skills-authoring` (requirement text) + `scripts/validate-skills.py` C5 docstring | already canonical — skills carry the block, not the rule |
| Where a skill's version moves and why | `skills-authoring` *A skill's version moves with its content* | already canonical — patch bumps, no restating |

## Risks / Trade-offs

- [A pin against a public stub or source tree reads as a runtime pin] → the block names the artifact
  probed (`acc-lua-sdk @ <sha>`, `AssettoServer source at v0.0.55-pre25`) and says the runtime was not
  run; the reviewer sees the boundary in the block itself.
- [`defers` phrase becomes a loophole for code-heavy skills] → it is the phrase that already exists,
  used by one skill (`helm-migration`); the selftest mutation (c) uses a skill without it, so a skill
  that adds the phrase to dodge C5 is a review finding, not a silent pass.
- [Catalog-wide C5 fails an unrelated future skill that forgot the block] → intended: that is the
  gate the issue asks for; the finding names both exits.
- [The `assettoserver-plugin` disclosure widens into a doctrine rewrite mid-run] → scope-change
  protocol: it is recorded as a follow-up in E.4 and the block states the contradiction only.

## Open Questions

- Which CSP build the DriveZone servers require: not found on this machine (the server image carries
  no `extra_cfg.yml`, `~/works` holds no DriveZone config). The `assettoserver-csp-lua` block will
  name the SDK commit probed and leave the build number as an explicit gap unless the user supplies it.
