## Context

`openspec/specs/skills-authoring` already carries four requirements whose common subject is
"do not assert what you did not check": *Verified enforcement claims*, *Simulated failure
behaviour*, *Versioned external APIs are pinned*, *No runtime is not an excuse*. All four bind the
**author** of a skill. None binds the **agent running** one.

The evidence that the runtime half is missing is mechanical, not editorial:

```
$ grep -rniE 'websearch|webfetch' skills/ | wc -l
0
$ grep -rniE '\bresearch\b' skills/ | wc -l
0
```

Probed at HEAD `c965689` on 2026-08-06 over 32 skills.

## Goals / Non-Goals

**Goals:**

- One canonical, stack-agnostic home for claim verification at execution time.
- A ladder cheap enough to run on real work: it must have a stop condition and an explicit "do not
  run me" case, or it becomes ceremony and gets skipped wholesale.
- A not-found report that is a *deliverable*, so "I could not find it" stops being a failure state
  and starts being an acceptable answer.
- Scope fidelity in the same skill, because delivering unrequested work is the same defect wearing
  different clothes — an unverified claim about what the user wanted.

**Non-Goals:**

- Enforcing the doctrine mechanically. No validator check is added here; the mechanical layer is a
  separate change (rite gate + hook) with its own honest limits.
- Making the doctrine apply to every sentence. Over-labelling produces decorative citations, which
  is the failure mode this skill is supposed to prevent, self-inflicted.
- Removing any stack-specific instance of the rule from a sibling skill. Those are instances, not
  duplicates, and the authoring spec explicitly permits them when they link.

## Decisions

**The name is `verify-before-claiming`.** Alternatives considered:
`research-first` names an activity rather than a prohibition — researching and then guessing anyway
is exactly the reported failure, and it competes with `documentation`, which already promises
read-the-code-first. `evidence-first` collides with a word this catalog has already defined
narrowly: `execute-backlog/references/acceptance-tracking.md` fixes *evidence* as "a test name, a
command output line, a migration result, a diff path". `no-guessing` matches `backlog`'s existing
literal but routes badly — a model rarely thinks "I am about to guess" — and every other name in
the catalog is a topic or an action, never a prohibition.

**A claim is defined to include acting, not only asserting.** This is load-bearing and is the first
sentence of the skill. Without it the name reads as answer-hygiene and the off-script guard has no
home; with it, building an endpoint nobody asked for is a claim about intent and falls under the
same rule. This is what keeps the change to one skill instead of two.

**The ladder is ordered by cost and forbids skipping downward.** Searching the web for something
the repo answers is both slower and more often wrong, because the web does not know *this* project.
Rungs 4-5 are made dependent on rung 2: fetching `latest` documentation against a pinned older
dependency is the highest-yield way to produce a confident wrong answer, so the version comes first
and the documentation URL is built from it.

**`metadata.category: process`.** `generate.sh:163-168` maps `git|process → workflow`, so the skill
ships in the existing `ai-skills-workflow` bundle. Inventing a category would cost a CI whitelist
edit, a `skills-authoring` spec delta, a `GROUP_DESC` entry and a new marketplace plugin — to ship
anti-guessing doctrine in a bundle nobody enables.

**The anti-pattern catalog ships small and sourced.** `skills-authoring` → *Checklists are scored
against field defects* states "A checklist item without a traceable origin SHALL NOT be added", so
every row carries the defect that earned it, and every seed row is citable inside this repository.
Nine sourced rows beat thirty plausible ones.

**No mechanical enforcement in this change.** A provenance ledger checked by CI was designed and
rejected: CI can only prove such a ledger is well-typed, so a fabricated row passes every check and
leaves the reader trusting the skill *more*. That converts an obvious defect into a certified one.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Claim verification, research ladder, not-found reporting, knowledge-cutoff, off-script scope guard | `verify-before-claiming` | **new canonical home**; added to the `skills-authoring` canonical map |
| "Only document what you read / admit the gap" | `verify-before-claiming` | **move** from `documentation/SKILL.md:34-36`, which shrinks to one line + link |
| "No invention" for GitHub org/repo/Project/field metadata | `backlog` | already canonical (domain instance) — gains a link to the general form |
| "Never guess missing scope" on an incomplete item; "run only discovered commands" | `execute-backlog` | already canonical (rite instance) — gains links to the general form |
| Scope-deviation bookkeeping (issue comment, board column) | `execute-backlog` | already canonical — the new skill's off-script guard links out to it rather than restating it |
| "Consult the SDK — never guess an API" (CSP EmmyLua stubs) | `assettoserver-csp-lua` | already canonical (stack instance) — gains a link |
| Two-contract version pinning against the runtime tag | `assettoserver-plugin` | already canonical (build-time instance) — gains a link |
| "The chart template is the source of truth, not this skill" | `helm-migration` | already canonical (stack instance) — gains a link |
| Adversarial methodology (breaking a change after it is written) | `bug-hunter` | already canonical — the new skill links to it as the *after* half; no methodology restated |
| REST negative/fuzz/contract checklist | `api-resilience-testing` | already canonical — gains a link about measuring a baseline before asserting a status code |
| OpenSpec lifecycle | `openspec` | already canonical — untouched |

No mechanism list from a sibling skill is reproduced inline. Every entry above marked "already
canonical" keeps its full text and receives exactly one sentence plus a link.

## Risks / Trade-offs

- **Research theater** (a visible search, an answer still from memory) → Ground rule *Cite only what
  you opened*, with the operational test "if you cannot quote a line from it, you did not read it",
  and the not-found report that logs commands rather than narration.
- **Fabricated citations** — strictly worse than no citation, because they make wrong output more
  authoritative → `file:line` must come from a tool result in this session; citing the command that
  reproduces a fact is preferred over citing its location, because the reader can re-run it; a
  citation that cannot be re-derived is downgraded to *inferred*. The skill states plainly that
  prose cannot fully mitigate this, and that no gate in this repo catches it in chat.
- **Cost on trivial work** → the cost-rule table carries an explicit "no ladder" row, and the ladder
  stops at the first rung that answers.
- **Networkless environments** → rungs 0-3 always exist; missing rungs are named in the report and
  the run jumps to asking the user. Declared in `compatibility`, which is readable before the skill
  is even loaded.
- **Routing dilution** — a description matching every prompt is either always loaded or never
  selected → the description is scoped to correction moments and decision moments and carries four
  `Do NOT use for` boundaries.
- **The skill's own claims going stale** → every command it prescribes was probed on this machine
  and the versions and date are recorded in the skill body, per *Versioned external APIs are pinned*.

## Migration Plan

Additive. No skill is renamed or removed, so no existing cross-reference breaks and
`scripts/validate-skills.py` C2/C7 stay green. The catalog grows from 32 to 33 skills, so the
README row and the two bundle descriptions that *name* the workflow skills are updated here.

The published skill **counts** (`.claude-plugin/marketplace.json` says 27, `README.md` says 30) are
already wrong today and are deliberately **not** touched by this change: they are the subject of a
sibling change and fixing them here would be exactly the unrequested scope this skill's own
off-script guard forbids. Correcting a drifted count is not a prerequisite for adding a skill.

Rollback is `git revert` of the single commit plus `./generate.sh`.

## Open Questions

None outstanding. The one question that would have been open — whether to enforce provenance
mechanically — was answered by designing the enforcement and rejecting it on the grounds recorded
under *Decisions*.
