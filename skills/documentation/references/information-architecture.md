# Reference — information architecture

The rest of this skill governs whether a claim in a document is **verifiable**. This file governs
whether the document is **navigable**. A reader cannot check a fact they cannot find, so the two
obligations are the same obligation seen from two sides.

Seven rules. Each carries a published source, because a rule invented in-house is a preference with
a table around it. Each also carries a verdict — **with validator** or **review-only** — and a
review-only verdict is never a bare label: it carries the measurement that produced it.

The measurement was taken on `solvelab/ferdinand@66346d4`, a repository documented under this skill,
with `references/check-doc-structure.py`. Findings were confirmed by hand, one at a time. The
sample is one repository with one writing style; that is a limit of the number, recorded rather than
hidden.

| Rule | What it says | Verdict |
|---|---|---|
| [R1](#r1--a-navigated-document-carries-an-index) | index above 100 lines, covering every `##` | with validator |
| [R2](#r2--a-table-cell-stops-at-120-characters) | no table cell over 120 characters | with validator |
| [R3](#r3--a-catalog-past-25-options-is-navigated-not-scanned) | past 25 options, index plus one section each | with validator |
| [R4](#r4--an-option-entry-repeats-the-same-fields-in-the-same-order) | fixed anatomy, fixed order | with validator |
| [R5](#r5--reference-describes-the-why-is-a-link) | reference describes; the why is a link | review-only |
| [R6](#r6--a--belongs-to-the--above-it) | a `###` belongs to the `##` above it | review-only |
| [R7](#r7--an-alert-uses-a-type-github-renders) | alerts use the five GitHub types | with validator |

## R1 — a navigated document carries an index

A document over **100 lines** carries an index, and the index links every `##` in the document.

Source: the [Standard README specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
makes a table of contents required, optional only for READMEs under 100 lines, and requires it to
capture all level-two headings. Google's
[Markdown style guide](https://google.github.io/styleguide/docguide/style.html) asks for a `[TOC]`
directive "unless all of your content is above the fold on a laptop".

The rule judges a document readers **navigate**. A one-shot record — a spike note, an ADR, a
post-mortem — is read start to finish and owes no index. Nothing in the text distinguishes the two,
so the consumer draws that line with `--exclude`.

```markdown
<!-- defect: 1006 lines, and the first `##` is the only way to find anything -->
# Ferdinand
Watchdog out-of-band de nodes Kubernetes.

## Tech Stack
```

```markdown
<!-- correct: one entry per `##`, right after the opening -->
# Ferdinand
Watchdog out-of-band de nodes Kubernetes.

## Índice

- [Quick Start](#quick-start)
- [Como funciona](#como-funciona)
- [Configuração](#configuração)
```

**Verdict: with validator.** Measured 10 findings; 7 confirmed, 3 false positives — all three spike
notes just over the threshold, which is a scope question rather than an accuracy one and is what
`--exclude` exists for. With the exclusion, 7 findings and 7 confirmed.

Two detector defects were found by that hand pass and fixed: an index heading written `## Índice`
was read as absent because the match was not accent-folded, and the index heading was reported as
missing a link to itself.

## R2 — a table cell stops at 120 characters

No cell in a pipe table carries more than **120 characters**.

Source: Google's Markdown style guide names the failure directly — a bad table shows "poor column
distribution, unbalanced dimensions, or rambling prose within cells", and "avoid using tables when
your data could easily be presented in a list".

A cell cannot wrap, so prose in a cell is a paragraph rendered as one unbroken line. Whatever the
reader needed most — the accepted range, the consequence — ends up at the far right of it.

```markdown
<!-- defect: 205 characters, and the accepted range is at the end of it -->
| `KUBELET_STATS_PORT` | `10250` | porta do kubelet. Configurável por um motivo só: o kubelet do `kind` usa certificado autoassinado, e sem esta porta a quebra de disco não teria como ser exercitada antes do merge. Aceita `1`–`65535` |
```

```markdown
<!-- correct: the row scans, the detail is a section -->
| [`KUBELET_STATS_PORT`](#kubelet_stats_port) | `10250` | porta do kubelet |
```

**Verdict: with validator.** Measured 15 findings, 15 confirmed, 0 false positives. The count was
reproduced independently by an `awk` pass over the same file, which is why this rule shipped with a
gate rather than a report.

## R3 — a catalog past 25 options is navigated, not scanned

Up to **25 rows** of uniform data stays a table. Above that, or with prose in any cell, it becomes an
index plus **one section per option**, so every option gets an anchor.

Source: the same Google rule, from the other direction — a table is right for uniform data scanned
quickly. The section form at scale is what
[Grafana's configuration reference](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/)
does: `###` per section, `####` per option, each with its own type, default and description.

A heading is an anchor. `docs/REFERENCE.md#leader_term` can be pasted into an issue, a runbook or an
alert message; a table row cannot, and it never appears in the GitHub Outline either.

The count is per table **and** per document. A per-table threshold alone is evaded by splitting one
catalog across many small tables, which leaves every option unanchored just the same.

**Verdict: with validator.** Measured 1 finding, 1 confirmed: 115 option rows across one document
with not one option heading. The per-document arm exists because of that measurement — the per-table
arm alone scored zero on the very file the rule was written for.

## R4 — an option entry repeats the same fields in the same order

Every option entry carries the same fields, in the same order: **Tipo · Padrão · Faixa · Recarrega**,
then the description, then an alert where there is risk, then where the value is read from.

Source: [Diátaxis on reference](https://diataxis.fr/reference/) — "reference material is useful when
it is consistent", and "standard patterns are what allow us to use reference material effectively".
Google's [API reference guidance](https://developers.google.com/style/api-reference-comments) fixes
the shape of a default the same way: state the behaviour per value, then the default.

An anatomy whose fields move around is six documents wearing one heading level.

```markdown
#### `DEADMAN_URL`

**Tipo** URL · **Padrão** — · **Recarrega** não

Endpoint do dead man's switch.

> [!CAUTION]
> Ausente ou vazia **reprova o boot**.

Lido em [`src/config/load.ts`](../src/config/load.ts)
```

A field that does not apply is omitted, never reordered. The order is what the check reads.

**Verdict: with validator.** No findings on the sample: the repository has no option sections yet,
because adopting them is the work this rule unblocks. The check is proved by its injected defect in
`--selftest`, not by the sample — and that distinction is the point of recording it here.

## R5 — reference describes; the why is a link

A reference page describes. The reason a default is what it is belongs to an explanation page, and
the reference links to it.

Source: Diátaxis — reference is "austere and uncompromising", its only purpose is "to describe, as
succinctly as possible, and in an orderly way", and it links out to how-to and explanation rather
than absorbing them. The practical argument is rot speed: a page mixing the two goes stale at the
speed of its faster half.

```markdown
<!-- defect: the reason lives in the reference, inside a table cell -->
| `COLLECTOR_THROTTLE_ENABLED` | `false` | desligado por escopo, não por custo: `cpu_throttled` mede um cgroup batendo no limite que o próprio pod declarou, e o node pode estar ocioso enquanto o sinal dispara |
```

```markdown
<!-- correct: the reference describes, the reason has an address -->
**Tipo** booleano · **Padrão** `false` · **Recarrega** sim

Liga o sinal de estrangulamento de cgroup.

> [!NOTE]
> Desligado por padrão por escopo. Ver [Sinais do coletor](SIGNALS.md#cpu_throttled).
```

**Verdict: review-only.** No validator ships. Telling a description from a justification is a
judgement about meaning, and the draft heuristic — causal markers such as "porque", "por um motivo",
"de propósito" — reproved correct prose, which is the failure mode that gets a gate switched off in
its first week. The same conclusion was reached in this catalog once before, for
*a prescribed verification states what passes*, where the draft flagged 4 lines and 3 were false
positives.

## R6 — a `###` belongs to the `##` above it

A heading is a tree, not a font size. Every `###` is a child of the `##` above it and is read that
way — by the GitHub Outline, by anyone scanning the sidebar, and by every agent that parses the
document.

Source: Google's Markdown style guide requires "unique and fully descriptive names for each
heading, even for sub-sections", and one `#` per document with everything below nested from `##`.

```markdown
<!-- defect: none of these three is about running without a cluster -->
## O modo sem cluster
### Credenciais
### Limites dos destinos
### Coordenação entre agentes
```

**Verdict: review-only.** A size signal ships — a `##` over 80 lines with four or more children is
**reported**, never failed — but no verdict does.

Measured 10 findings, **3 confirmed, 7 noise**: `## Memória` with four memory signals under it,
`## CPU` with five CPU signals, `## 4. Decisões de arquitetura` with four decisions, and
`## 1. Variáveis do agente` with fourteen variable groups are all correctly nested and merely long.
Seven wrong reports in ten is a gate nobody keeps, so the rule ships as a rule and the script ships
as a pointer to review.

## R7 — an alert uses a type GitHub renders

GitHub renders exactly five alert types: `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION`. Anything
else renders as a plain blockquote, silently.

Source: [GitHub's formatting documentation](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).

Alerts are placed at the point of danger, not in a distant section. `<details>` is for a long block
a reader chooses to open, never for something they must read. Neither is decoration: an alert that
carries no risk trains the reader to skip the one that does.

**Verdict: with validator.** No findings on the sample — the repository uses no alerts at all yet,
which is itself the gap R7 exists to close. Proved by its injected defect in `--selftest`.

## Running the check

```bash
python3 skills/documentation/references/check-doc-structure.py --exclude 'spikes/*' README.md docs/
```

Exit code 1 when anything is reported, 0 when nothing is, 2 on a usage error. `--list` prints which
rules are implemented; `--rules R1,R2` runs a subset; `--selftest` injects one known defect per check
and asserts detection.

`--selftest` is the only gate over this script: `scripts/validate-skills.py` walks
`references/*.md` and never opens a `.py`, so a check that quietly stops firing is invisible to the
catalog's own validator and visible only here.

The existing `skills/code-locale/references/pre-commit-locale.sh` does **not** run this check — it
hardcodes two filenames and discovers no third detector. That is deliberate: document structure is a
property of the whole repository, measured once in CI, not per staged hunk. Wire it as a CI step, or
as a test in the repository's own suite.

## See also

- [`templates.md`](templates.md) — the skeletons these rules shape.
- The `verify-before-claiming` skill — why a rule ships with its measurement instead of its
  intention.
- The `code-locale` skill — why this file and the detector beside it carry English names while the
  documents they judge stay in their repository's language.
