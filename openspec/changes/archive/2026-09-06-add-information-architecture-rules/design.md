## Context

`skills/documentation/SKILL.md` is 203 lines with two references, `templates.md` and `examples.md`.
Its strength is verifiability: repo paths are links, a prerequisite states the value that passes,
env-var tables come from the config module, and the closing rule is *ship the checker*.

Its blind spot is organization. There is no rule about a table of contents, heading hierarchy, page
length, the anatomy of a reference page, or which GitHub-Flavored Markdown constructs mean something.

The four defects that motivated this change were all measured on `solvelab/ferdinand@66346d4`, a
repository documented under this skill, and none of them is reachable by any existing gate.

## Goals / Non-Goals

**Goals:**

- Seven organization rules, each traceable to a published source rather than to house preference.
- A per-rule verdict on automation, decided by a measured false-positive rate rather than by
  intention.
- A detector for the rules that survive that measurement, shipped with the skill so a consumer
  repository can wire it into its own CI.

**Non-Goals:**

- Editing any consumer repository. `solvelab/ferdinand#441` and `#442` do that and are blocked on
  this change.
- Wiring the detector into this catalog's CI. The rules govern documents in consumer repositories,
  not skills in this catalog; the catalog's own validator has a different subject.
- Rewriting `templates.md` and `examples.md` beyond the cross-link.

## Decisions

### The detector ships inside the skill, not in `scripts/`

`scripts/validate-skills.py` validates **skills in this catalog**. These seven rules judge
**documents in consumer repositories** — a README, a reference page, a runbook. Putting the checker
in `scripts/` would gate the wrong artifact and leave the right one unguarded.

The precedent is `code-locale`, which ships `references/check-identifier-locale.py` and
`references/check-prose-locale.py` for exactly this reason: the rule travels to the consumer, so the
checker travels with it. Alternative considered and rejected: extending `validate-skills.py` with a
`--docs` mode, which would make the catalog's validator answer two unrelated questions and give a
consumer repository no way to run the second one without cloning the catalog.

### The measurement decides which rules get a validator

This is the load-bearing decision, and it was learned in this same skill. When
*a prescribed verification states what passes* was proposed, the draft heuristic flagged 4 lines in
`docs/SETUP.md` of `solvelab/feldt` and **3 were false positives** — 1 real defect in 12. The rule
shipped review-only, and the published spec records that no validator covers it.

So the order here is: write the draft detector, run it against `ferdinand@66346d4`, count findings,
hand-confirm each, count false positives. The number decides. A rule whose detector is unreliable
ships review-only **with the count written beside it**.

R5 (*reference describes; the why is a link*) and R6 (*`###` belongs to the `##` above*) are the two
most likely to land there: both ask a question about meaning, and meaning has no fixed shape. The
change does not pre-decide their verdict — it measures them like the rest — but the design records
the expectation so a reviewer can check it against the outcome.

Alternative considered and rejected: promising seven validators and dropping the ones that turn out
unreliable during implementation. That is the same decision made silently instead of in writing, and
a silent drop is how a rule ends up looking covered when it is not.

### Table or section is a threshold, not a doctrine

A table is the right form for uniform multi-dimensional data scanned quickly, and the wrong form
once a cell carries prose — the Google Markdown guide names *"rambling prose within cells"* as the
signature of a broken table. A per-option section buys a stable anchor, an entry in the GitHub
Outline, and room for a footgun alert at the point of danger.

Both are correct in their range, so the rule carries a cut rather than a preference: **up to 25 rows
of uniform data stays a table; above that, or with prose in a cell, it becomes an index plus one
section per option.** Grafana's configuration reference is the exemplar for the section form at
scale.

### The detector carries `--selftest`, because the catalog's own validator cannot see it

Measured on `ai-skills@0959ccc`: `scripts/validate-skills.py` iterates `refs_dir.rglob("*.md")` and
never opens a `.py` under `references/`. Its C9 identifier-locale check runs
`check-identifier-locale.py --markdown-fences skills/`, which reads language-tagged fences inside
`*.md` only — its own KNOWN LIMIT says executable references are not scanned.

So a detector shipped here has **no catalog gate over its source**. The only thing that can prove its
checks still fire is a self-test it carries itself, which is also what the `skills-authoring`
requirement *Authoring rules are machine-enforced* demands of a rule-enforcing script: one injected
defect per check, asserting detection. `check-identifier-locale.py --selftest` is the house form and
this detector follows it.

### The script reaches consumers through `plugins/` and the clone, not through every wrapper

`generate.sh` propagates unevenly, and the difference is not cosmetic:

| Output | What a new `references/` file gets |
|---|---|
| `plugins/` | the whole skill directory copied verbatim — the `.py` arrives byte-for-byte |
| `cursor/` | a rewritten blob link, but **only if `SKILL.md` links the file** |
| `claude/`, `copilot/` | a directory-level pointer; no per-file link |
| `codex/` | an include of `SKILL.md`; `references/` is never mentioned |

Two consequences the change has to respect. First, `SKILL.md` must link
`information-architecture.md` — `validate-skills.py`'s C11 fails an orphan `*.md` under
`references/`, and the Cursor link depends on the same edge. Second, a consumer that installs
through a thin wrapper reaches the detector by path, not by copy, so the reference states how to run
it from a clone rather than assuming it was vendored.

### The pre-commit hook does not pick this detector up

`skills/code-locale/references/pre-commit-locale.sh` hardcodes exactly two filenames —
`check-identifier-locale.py` and its sibling `check-prose-locale.py` — and refuses the commit when
the second is missing. A third detector in that directory is **not** discovered by it.

That is the right behaviour to leave alone: the locale hook gates identifiers and prose on every
commit, while document structure is a repository-wide property better measured once in CI than on
each staged hunk. The reference therefore prescribes CI wiring, and says plainly that the existing
pre-commit hook does not run it — rather than leaving a reader to assume it does.

### The anatomy is fixed in order, not only in content

Diátaxis calls consistency the property that makes reference material usable: *"standard patterns
are what allow us to use reference material effectively."* An anatomy whose fields vary in order
reads as six different documents. The order is **Tipo · Padrão · Faixa · Recarrega**, then the
description, then the alert, then `Lido em` — and the detector can only check a shape that is fixed.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Document organization: index, heading tree, page anatomy, GFM vocabulary | `documentation` | already canonical — this change gives it the rules it was missing |
| Research a fact before asserting it; report the gap instead of substituting | `verify-before-claiming` | link — the measurement discipline behind "the number decides" is cited, not restated |
| Identifier and file names are English; prose follows the repo's language | `code-locale` | link — `check-doc-structure.py` and `information-architecture.md` take their names from this rule, which is not restated here |
| A rule the catalog publishes as review-only records its measurement | `skills-authoring` (spec) | move — the obligation is stated once in the capability spec; the `documentation` skill links to it rather than repeating it |
| Reference describes, explanation explains (Diátaxis four modes) | `documentation` | already canonical — the existing *One purpose per page* section owns it; the new reference links to it instead of restating the four modes |

## Risks / Trade-offs

- Seven rules do not become seven validators → the measurement is an acceptance criterion, and
  `review-only` with a recorded count is a legitimate outcome, not a failure of the change.
- A detector that reproves correct documents is switched off in its first week, leaving the rule
  worse off than with no gate → a high false-positive rate reproves the detector, never the sample
  repository.
- The detector grows into a second `check-identifier-locale.py`, which is 981 lines → the subject
  here is markdown structure (headings, tables, anchors), not morphology; passing roughly 350 lines
  is read as a signal that one rule is being forced into a shape it does not have.
- The sample is a single repository, so the false-positive rate is measured on one writing style →
  recorded as a limit of the measurement rather than hidden; a second sample repository is a
  follow-up, not a blocker.
- A detector whose own source no catalog check reads can rot silently → `--selftest` is the only
  gate over it, so a check that stops firing has to fail the self-test, and the self-test runs in the
  Simulation group of this change rather than being promised for later.
- R1's index rule can itself rot, since an index is another list somebody maintains → it is the rule
  most cheaply automated, and it is expected to ship with a validator that compares the index
  against the `##` headings.

## Open Questions

- Whether the anchor GitHub generates for a heading whose text is a code span keeps the backtick
  content. It does in `solvelab/feldt`, measured there against returned HTML, but it has not been
  probed for this catalog's own rendering and is recorded here rather than asserted.
