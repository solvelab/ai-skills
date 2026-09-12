# Reference — information architecture

The rest of this skill governs whether a claim in a document is **verifiable**. This file governs
whether a reader can **find** it. A reader cannot check a fact they cannot find, so the two
obligations are the same obligation seen from two sides.

Fourteen rules in two families, because "can I find it" has two halves. **R1-R7** ask whether one
page is navigable. **L1-L7** ask whether the repository puts its documents where the map says, and
each fact in the document that owns it — a perfectly navigable page is unreachable if it is the
third document about the same subject, under a name only this repository uses.

Each rule carries a published source, because a rule invented in-house is a preference with a table
around it. Each also carries a verdict — **with validator** or **review-only** — and a review-only
verdict is never a bare label: it carries the measurement that produced it.

The page rules were measured on `solvelab/ferdinand@66346d4`, one repository with one writing
style, with `references/check-doc-structure.py`. The layout rules were measured on 2026-09-12 across
**10 repositories** of a maintainer's fleet, with `references/check-doc-layout.py`: 64 findings, 63
confirmed by hand, 1 false positive. Findings were confirmed one at a time, in both families.

## Index

| Rule | What it says | Verdict |
|---|---|---|
| [R1](#r1--a-navigated-document-carries-an-index) | index above 100 lines, covering every `##` | with validator |
| [R2](#r2--a-table-cell-stops-at-120-characters) | no table cell over 120 characters | with validator |
| [R3](#r3--a-catalog-past-25-options-is-navigated-not-scanned) | past 25 options, index plus one section each | with validator |
| [R4](#r4--an-option-entry-repeats-the-same-fields-in-the-same-order) | fixed anatomy, fixed order | with validator |
| [R5](#r5--reference-describes-the-why-is-a-link) | reference describes; the why is a link | review-only |
| [R6](#r6--a--belongs-to-the--above-it) | a `###` belongs to the `##` above it | review-only |
| [R7](#r7--an-alert-uses-a-type-github-renders) | alerts use the five GitHub types | with validator |
| [L1](#l1--every-always-slot-is-present-or-declared-absent) | every always-slot present, or declared | with validator |
| [L2](#l2--a-legacy-name-is-reported-with-its-destination) | a legacy name carries its destination | with validator |
| [L3](#l3--the-root-carries-the-entry-documents-and-nothing-else) | nothing loose at the root | with validator |
| [L4](#l4--a-record-of-one-moment-lives-with-the-other-records) | dated records live in `docs/reports/` | with validator |
| [L5](#l5--a-file-name-is-english) | file names are English | with validator, delegated |
| [L6](#l6--the-mirror-matches-the-source-in-structure) | the mirror matches in structure | with validator |
| [L7](#l7--a-fact-appears-in-the-document-that-owns-it) | a fact lives in its owning document | with validator |

Then: [The layout rules](#the-layout-rules) · [Running the checks](#running-the-checks) ·
[See also](#see-also).

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

Source: Google's [Markdown style guide](https://google.github.io/styleguide/docguide/style.html) names the failure directly — a bad table shows "poor column
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

Source: the same Google [Markdown style guide](https://google.github.io/styleguide/docguide/style.html) rule, from the other direction — a table is right for uniform data scanned
quickly. The section form at scale is what
[Grafana's configuration reference](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/)
does: `###` per section, `####` per option, each with its own type, default and description.

A heading is an anchor. `docs/REFERENCE.md#leader_term` can be pasted into an issue, a runbook or an
alert message; a table row cannot, and it never appears in the GitHub Outline either.

```markdown
<!-- defect: 101 options, every one of them unreachable by link -->
| Variável | Padrão | Descrição |
|---|---|---|
| `DEADMAN_URL` | — | **obrigatória**. Endpoint do dead man's switch |
| `FERDINAND_LABELS` | — | **obrigatória**. `chave=valor,...` |
<!-- … 99 more rows, no heading anywhere -->
```

```markdown
<!-- correct: the table scans, the section is the address -->
| Variável | Padrão | Em uma linha |
|---|---|---|
| [`DEADMAN_URL`](#deadman_url) | — | dead man's switch |

#### `DEADMAN_URL`

**Tipo** URL · **Padrão** — · **Recarrega** não

Endpoint do dead man's switch.
```

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
<!-- defect: three entries, three shapes — the reader re-learns the page at every heading -->
#### `HEALTH_PORT`
Porta de `/healthz`. Padrão `8080`.

#### `LEADER_TERM`
**Padrão** `30m` · **Tipo** duração
Mandato do líder.

#### `STATE_DEBOUNCE`
Coalescência das escritas. Aceita duração; o padrão é `1s`.
```

```markdown
<!-- correct: the same fields, in the same order, every time -->
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

Source: [Diátaxis on reference](https://diataxis.fr/reference/) — reference is "austere and uncompromising", its only purpose is "to describe, as
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

Source: Google's [Markdown style guide](https://google.github.io/styleguide/docguide/style.html) requires "unique and fully descriptive names for each
heading, even for sub-sections", and one `#` per document with everything below nested from `##`.

```markdown
<!-- defect: none of these three is about running without a cluster -->
## O modo sem cluster
### Credenciais
### Limites dos destinos
### Coordenação entre agentes
```

```markdown
<!-- correct: each subsection under the parent it is actually about -->
## Configuração
### Identidade do ambiente é obrigatória
### Credenciais
### `NODE_EXTRA_CA_CERTS` não é opcional

## Modo sem cluster
### Onde o estado é guardado sem ConfigMap
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

```markdown
<!-- defect: GitHub knows no DANGER, and renders this as a grey quote nobody reads as a warning -->
> [!DANGER]
> Declarar esta variável reprova o boot.
```

```markdown
<!-- correct: one of the five, at the point of danger -->
> [!CAUTION]
> Declarar esta variável **reprova o boot**: ela saiu na `v1.44.0`.
```

Alerts are placed at the point of danger, not in a distant section. `<details>` is for a long block
a reader chooses to open, never for something they must read. Neither is decoration: an alert that
carries no risk trains the reader to skip the one that does.

**Verdict: with validator.** No findings on the sample — the repository uses no alerts at all yet,
which is itself the gap R7 exists to close. Proved by its injected defect in `--selftest`.

## The layout rules

The page rules above judge one document. These judge the repository: whether the documents the map
names exist, are called what the map calls them, sit where it puts them, and hold the facts they own.

The measurement behind every verdict below was taken on 2026-09-12 with
`references/check-doc-layout.py` over 10 repositories of a maintainer's fleet — `feldt`,
`ferdinand`, `k8s-troubleshoot-bot`, `filial-backend-rest-api`, `filial-amazon`,
`fabcost3d-mqtt-agent`, `fabcost3d-backend-rest-api`, `talk-to-me`, `speak-memo-backend`,
`kokoro-tts-server` — all documented under earlier versions of this skill.

| Rule | Findings | Confirmed | False positives |
|---|---|---|---|
| L1 | 13 | 13 | 0 |
| L2 | 38 | 38 | 0 |
| L3 | 3 | 2 | 1 |
| L4 | 4 | 4 | 0 |
| L5 | 5 | 5 | 0 |
| L6 | 0 | — | — |
| L7 | 1 | 1 | 0 |
| **Total** | **64** | **63** | **1** |

One more false positive existed and was fixed before this run rather than counted in it: a root
`CLAUDE.md` was reported as a loose document, which is wrong — it is an agent-instruction file, a
class the skill itself names. The root allowlist gained `CLAUDE.md`, `GEMINI.md` and GitHub's
community-health files, and the run above is the one after that fix. Recording it here rather than
quietly dropping it is the point: a measurement that only reports the findings the tool survived is
a measurement of the tool's confidence, not of its accuracy.

## L1 — every always-slot is present, or declared absent

Two documents are owed by every project: `README.md` and `docs/en/REQUIREMENTS.md`. The README owes
a `## Documentation` section listing every slot. A slot the project does not earn is written
`not applicable: <reason>`; a slot that is simply missing, with no line about it, is reported.

Source: the [Standard README specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
requires the README to carry the project's own table of contents; [Diátaxis](https://diataxis.fr/)
treats the four needs as a set the reader expects to find, not as a menu the author draws from.
`ISO/IEC/IEEE 29148` is the reason requirements are unconditional: a system that cannot say what it
is for cannot say whether it works.

```markdown
<!-- defect: the reader cannot tell "we decided against it" from "nobody wrote it" -->
## Documentation

- [Setup](docs/en/SETUP.md)
```

```markdown
<!-- correct: every slot appears, the absent ones with their reason -->
## Documentation

- [Requirements](docs/en/REQUIREMENTS.md)
- [Setup](docs/en/SETUP.md)
- Operations — not applicable: one environment, started by one command
```

**Verdict: with validator.** Measured 13 findings, 13 confirmed: 10 repositories with no
requirements document at all, and 3 with no documentation index. Not one of the 39 repositories in
the wider survey carried either. A conditional slot is never reported as missing — whether a project
earns an API reference is a fact about its code, and a script that guessed it would reprove the
projects that correctly have none.

## L2 — a legacy name is reported with its destination

A document under a name the map absorbs, or under the right name in the wrong place, is reported
together with the canonical path it migrates to.

Source: the rule is this catalog's own, and its evidence is the survey in the change that introduced
it — 19 `docs/TECHNICAL.md` against 12 `ARCHITECTURE.md`, 11 repositories carrying both at once, six
names for the operation slot. Naming a destination rather than a defect follows
[Google's guidance on error messages](https://developers.google.com/style/error-messages): say what
to do, not only what is wrong.

```text
docs/TECHNICAL.md: [L2] legacy name for the explanation slot -> docs/en/ARCHITECTURE.md
docs/RUNBOOK.md:   [L2] legacy name for the operation slot   -> docs/en/OPERATIONS.md
```

**Verdict: with validator.** Measured 38 findings, 38 confirmed, across all 10 repositories. This is
the highest-volume rule by a wide margin, and that is the point: it is measuring a migration, not a
defect rate, and it goes quiet once the migration is done.

## L3 — the root carries the entry documents and nothing else

The root holds `README.md` and its mirror, `AGENTS.md` and the other agent-instruction files,
`CHANGELOG.md`, `CONTRIBUTING.md`, and GitHub's community-health files. Every tier document lives
under `docs/<tree>/`; every transient record under `docs/reports/`.

Source: [GitHub's community profile](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions)
fixes which files it reads from the root and only from the root; the Standard README specification
gives the README the job of pointing at everything else.

**Verdict: with validator.** Measured 3 findings, 2 confirmed, 1 false positive. The false positive
is `NOTICE-fork.md` in a repository that forks an upstream project: it is a provenance notice, a
variant of `NOTICE.md`, which the allowlist accepts under its own name. Fork-provenance files are
what `--exclude` is for, the same exit R1 uses for spike notes. The two confirmed findings were a
second README (`README-fork.md`) and a tier document left at the root (`CICD_SETUP.md`).

## L4 — a record of one moment lives with the other records

A file whose name carries a date, or a marker of a single occasion — a homologation, a diagnosis, a
validation report, a progress note — belongs in `docs/reports/YYYY-MM-DD-<slug>.md` and nowhere else.

Source: [Diátaxis](https://diataxis.fr/) separates documentation by the reader's need, and a record
of one moment serves none of the four: nobody learns, does, looks up or understands from it. It is
evidence, kept for provenance. Mixing it into the documentation directory is what teaches a reader
that the directory cannot be trusted to be current.

**Verdict: with validator.** Measured 4 findings, 4 confirmed: two validation reports at a
repository root and two re-validation write-ups inside `docs/`. In the wider survey of 39
repositories the same pattern appears 21 times, including 12 homologation records in one workspace.

## L5 — a file name is English

File and directory names are the machine layer: English, whatever language the prose inside them is.

Source: the `code-locale` skill, which is the canonical home of that rule for this catalog, and which
already carries the waiver protocol (`.identifier-locale-allow`).

**This rule owns no word list.** It shells out to
`skills/code-locale/references/check-identifier-locale.py` and raises that script's verdicts. When
the sibling cannot be found, L5 reports itself **NOT RUN** instead of reporting clean — a rule that
answers "no findings" because its engine is missing is worse than a rule that is absent, because it
is believed.

Only verdicts are raised, never the advisory tier. Probed 2026-09-12: a name built on a Portuguese
verb ending is a `path-pt-morphology` verdict and is reported; a name whose first segment is merely
absent from the English word list is advisory there, and staying advisory here is what keeps product
names from being reproved. Known names of that second kind — `COMO-SUBIR.md` is the one the fleet
carries — are caught by L2 through the map's legacy list, which also says where they go.

**Verdict: with validator, delegated.** Measured 5 findings, 5 confirmed, 0 false positives.

## L6 — the mirror matches the source in structure

Two languages are the default. Every document under `docs/en/` has a twin under the mirror tree with
the same file name, the same number of `##` sections, the same section numbering, and the same fenced
code blocks byte for byte. A project that documents in one language on purpose says so in the README
index (`documented in English only`); a source tree with no mirror and no such line is reported,
because a reader cannot otherwise tell a decision from an abandoned migration.

Source: the [W3C's guidance on localized sites](https://www.w3.org/International/questions/qa-mlsite-navigation)
treats a translated page as the same page in another language, navigable the same way;
[GitLab's handbook](https://handbook.gitlab.com/handbook/) is one large public example of the
single-source-plus-translation model this rule assumes.

What the rule does **not** judge is whether the translated prose still says what the source says.
That is a judgement about meaning across two languages, and this catalog has measured twice what a
gate over meaning costs: 7 of 10 findings wrong for heading nesting (R6) and 3 of 4 for
justification prose (R5). Translation freshness is therefore **review-only**, and the mechanical
part of it is already covered by the rule that the pair is written in one commit.

**Verdict: with validator, proved only by its self-test.** Zero findings on the fleet, because not
one of the 10 repositories has a `docs/en/` tree at all yet — every one of them is still at the stage
L2 reports, and adopting the pair is the work this rule unblocks. Like R4 and R7 before it, the rule
is proved by its injected defects (a missing twin, a mirror whose code block was translated, and a
lone source tree with no declaration) rather than by the sample, and saying so is the difference
between a measurement and a claim.

## L7 — a fact appears in the document that owns it

Each kind of fact has one owning document. The checker recognizes an owned table by its canonical
header row and reports that row wherever it appears outside its owner.

Source: [Diátaxis on the four needs](https://diataxis.fr/) — a fact serving two needs at once is two
copies with one maintainer; Google's
[Markdown style guide](https://google.github.io/styleguide/docguide/style.html) makes the same point
about duplication between documents.

```markdown
<!-- defect: the same six rows, in README.md and in docs/SETUP.md, of one real repository -->
| Comando | O que faz |
|---|---|
| `make dev` | build + start + tail logs |
```

**Verdict: with validator.** Measured 1 finding, 1 confirmed — and the finding is the rule's own
worked example: `k8s-troubleshoot-bot` carries an identical six-row command table in `README.md:103`
and `docs/SETUP.md:58`. They have not drifted yet. That is what the rule is for: the copies agree
until the day one of them is edited, and nothing anywhere signals which one that was.

The known escape is deliberate and named in the script's own `KNOWN LIMIT`: a table with improvised
columns is not recognized. Guessing what a table is about from its contents is the same class of
judgement that sent R5 and R6 to review-only.

## Running the checks

```bash
# is each page navigable?
python3 skills/documentation/references/check-doc-structure.py --exclude 'spikes/*' README.md docs/

# is the repository's layout the map?
python3 skills/documentation/references/check-doc-layout.py --exclude 'vendor/*' .
```

Both scripts share one contract: exit code 1 when anything is reported, 0 when nothing is, 2 on a
usage error. `--list` prints the rules; `--rules R1,R2` (or `--rules L2,L4`) runs a subset;
`--selftest` injects one known defect per rule and asserts detection. The layout script adds `--map`,
which prints the document map itself, and it never moves, renames or writes a file.

`--selftest` is the only gate over both: `scripts/validate-skills.py` walks `references/*.md` and
never opens a `.py`, so a check that quietly stops firing is invisible to the catalog's own
validator and visible only there.

The existing `skills/code-locale/references/pre-commit-locale.sh` does **not** run either check — it
hardcodes two filenames and discovers no third detector. That is deliberate: document structure and
repository layout are properties of the whole repository, measured once in CI, not per staged hunk.
Wire them as a CI step, or as a test in the repository's own suite.

## See also

- [`templates.md`](templates.md) — the skeletons these rules shape, one per canonical document.
- The `verify-before-claiming` skill — why a rule ships with its measurement instead of its
  intention.
- The `code-locale` skill — why this file and the detector beside it carry English names while the
  documents they judge stay in their repository's language.
