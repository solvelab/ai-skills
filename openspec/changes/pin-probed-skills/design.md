## Context

Three audits established that a skill targeting a versioned external surface must say what it was
checked against, and C5 in `scripts/validate-skills.py` enforces it. Auditing the skills the earlier
passes had only validated mechanically exposed both halves of the problem: skills that were right but
unverifiable, and a detector that was wrong in both directions.

## Goals / Non-Goals

**Goals**
- Pin the skills whose external surface was actually probed, with what the probe produced.
- Fix the detector's false negatives and state its blind spot rather than paper over it.
- Leave a written record of the skills that remain unpinned, and why.

**Non-Goals**
- No pin for a surface that was not probed. That is the failure this requirement exists to prevent.
- No widening of the C5 trigger to catch prose claims — attempted, and it fires on every skill that
  merely names a tool. The limit is documented instead.
- No new doctrine in the pinned skills; only the pin block was added.

## Decisions

**D1 — Probe, then pin; never the reverse.** `fivem-nui-react` was pinned because a Vite build was run
with its four rules and each output checked. `assettoserver-csp-lua` was not, because nothing was run
against CSP. The asymmetry is the point.

**D2 — Record what the probe produced, not just the version.** "Verified against vite 8.2.0" is weaker
than naming the four outputs; the second is falsifiable by a reader in one command.

**D3 — Fix the detector's false negatives before adding pins.** It reported `assettoserver-plugin` and
`openspec` as unpinned when both carry explicit pins in forms the regex did not match
(`runtime 0.0.54 ↔ tag v0.0.54`, `Probed on CLI 1.6.0`). Adding pins to already-pinned skills would
have been noise created by the instrument — the same class of error the validator's first run produced
at scale.

**D4 — State the blind spot instead of guessing at it.** C5 only fires above 40 fenced lines. Widening
it to prose was tried and produced false positives on every skill mentioning a tool name. A check that
silently covers half its rule is worse than one that says which half — so the limit went into the
check's docstring and into the spec.

**D5 — Mark the fragment, don't rewrite it.** The one non-parsing `ts` block in `react-api-client` is
a legitimate excerpt (top-level `await` inside a mutation handler). It gets the same marker the `r3f-*`
family uses, not an invented wrapper that would change what it teaches.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Version-pin requirement and its enforcement | `openspec/specs/skills-authoring` + `scripts/validate-skills.py` | already canonical — detector fixed, limit declared |
| NUI build for CEF (Vite/terser rules) | `fivem-nui-react` | already canonical — pinned with probe output |
| `gh` Projects v2 recipes | `backlog/references/gh-projects.md` | already canonical — client version pinned |
| Executing a backlog item via `gh` | `execute-backlog` | already canonical — client version pinned |
| Excerpt marking convention for non-module code blocks | `r3f-*` family | convention reused, not restated |

## Risks / Trade-offs

- [Pinned versions age] → they name what was checked and when, which is falsifiable; the previous
  state was silently unverifiable. Re-probing is the maintenance action.
- [Four skills stay unpinned] → recorded explicitly in the proposal as a known gap, so the absence is
  a decision rather than an oversight.
- [C5 keeps its blind spot] → declared in the check and in the spec; skills below the threshold are
  hand-reviewed, which is how these three were found.
