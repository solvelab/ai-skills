## Why

The catalog already forces evidence when a skill is **written**: `openspec/specs/skills-authoring`
requires probe-tested tool claims, measured failure behaviour, pinned versions, and an audit even
when the runtime is absent. It forces nothing when a skill is **executed**.

That asymmetry is the whole gap. Measured on this catalog at HEAD `c965689`:
`grep -rniE 'websearch|webfetch' skills/` returns **0 hits** and `grep -rniE '\bresearch\b' skills/`
returns **0 hits** across all 32 skills. Every "verify first" instruction that does exist is a
local-filesystem instruction scoped to one stack — `assettoserver-csp-lua` ("Consult the SDK — never
guess an API"), `helm-migration` ("The chart template is the source of truth, not this skill"),
`backlog` step 3 (an Explore subagent over the local repo). None of them generalizes, and none of
them says what to do when the fact is not in the repo.

The two fragments closest to the rule are each trapped inside one skill:
`documentation/SKILL.md:34-36` ("A confident wrong sentence costs more than an admitted gap") is
scoped to writing docs, and `backlog/SKILL.md:41` ("**No invention** — never guess org, repo,
Project, field names or select options") is scoped to GitHub metadata.

So an agent using this catalog has no rule to consult before asserting an API, a flag, a config key
or a version, no defined way to report that it could not find one, and no guard against delivering
work nobody asked for. The defect this creates is not hypothetical — it has already landed inside
this repository, where three hand-copied counts drifted from the tree they describe (fixed by a
sibling change).

## What Changes

- Add `skills/verify-before-claiming/`, the canonical home for **execution-time** claim
  verification: a cheapest-first research ladder (session context → this repo → the installed
  dependency → the tool itself → version-pinned docs → web search → the user), verified/inferred/
  unknown claim labelling, a not-found report that lists the commands it ran, the knowledge-cutoff
  rule, and an off-script guard covering work the user did not ask for.
- The skill defines a **claim** as anything asserted *or acted on* as if true — which is what makes
  scope fidelity part of the same rule rather than a second skill.
- Ship three reference files: the per-ecosystem ladder commands, the output templates, and an
  anti-pattern catalog in which every row names the defect that earned it.
- Shrink `documentation/SKILL.md:34-36` to one line plus a link, moving the aphorism to the new
  canonical home; add a one-line link from eight sibling skills that state a stack-specific instance
  of the rule.
- Extend the `skills-authoring` canonical map so the new rule has a declared owner.
- **BREAKING for catalog consumers**: the catalog grows from 32 to 33 skills, which changes what
  `npx skills add solvelab/ai-skills --list` returns and adds a skill to the `ai-skills-workflow`
  plugin bundle.

## Capabilities

### New Capabilities

_None._ The behaviour belongs to the two existing capabilities below.

### Modified Capabilities

- `skills-authoring`: the canonical map gains an owner for claim verification, research and
  not-found reporting, so a sibling skill that states a stack-specific instance links instead of
  restating it.
- `skills-catalog`: the catalog gains a skill whose subject is the agent's own epistemics at
  execution time — the counterpart to the authoring-time evidence rules the specs already carry.

## Impact

- `skills/verify-before-claiming/` — new: `SKILL.md` plus `references/research-ladder.md`,
  `references/report-templates.md`, `references/failure-catalog.md`.
- `skills/documentation/SKILL.md` — the only doctrine that *moves*; lines 34-36 become a link.
- `skills/backlog`, `skills/execute-backlog`, `skills/bug-hunter`,
  `skills/api-resilience-testing`, `skills/assettoserver-csp-lua`, `skills/assettoserver-plugin`,
  `skills/helm-migration`, `skills/openspec-drivezone` — one link each, no doctrine removed.
- `README.md` — a new row in the Process & git table.
- `generate.sh` (`GROUP_DESC[workflow]`) and `.claude-plugin/marketplace.json` — the workflow
  bundle description names the new skill.
- Generated trees `claude/ codex/ cursor/ copilot/ plugins/` — rewritten by `./generate.sh`.
- Consumers of the `ai-skills-workflow` plugin receive one additional skill; nothing is removed or
  renamed, so no existing reference breaks.
