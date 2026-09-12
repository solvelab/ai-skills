# Simulation — what a real session leaves behind

The arm a green self-test cannot replace. Both cells ran on 2026-09-12 against the skill as
committed at `6a80f8d`, installed project-scoped at `.claude/skills/documentation/` — the layout
`generate.sh` publishes into `claude/skills/` — in a throwaway copy of a real repository with its
git history stripped and re-initialized.

```bash
claude -p "Documente este repositório. Siga a skill documentation." \
  --permission-mode acceptEdits --output-format json
```

`claude 2.1.269`, model as configured for the maintainer's own sessions. Nothing was written to any
real repository.

## Contents

- [Cell 1 — a service with no spec workflow](#cell-1--repo-plain-a-service-with-no-spec-workflow)
- [Cell 2 — a service that runs a spec-driven workflow](#cell-2--repo-openspec-a-service-that-runs-a-spec-driven-workflow)
- [Spend](#spend)
- [Verdict](#verdict)

## Cell 1 — `repo-plain`, a service with no spec workflow

Source: `editaudiotomovie/combine-audio`, a FastAPI service that concatenates audio with `ffmpeg`.
Before the run it carried `README.md` and `CHANGELOG.md` and nothing else.

**Observed**: 49 turns, 819 seconds, US$ 4.83. The session's closing report, verbatim at the top:

```text
Documentado. 13 arquivos, duas árvores.
```

### What appeared

```
README.md            README.pt-BR.md      CHANGELOG.md
docs/en/REQUIREMENTS.md   docs/pt-BR/REQUIREMENTS.md
docs/en/SETUP.md          docs/pt-BR/SETUP.md
docs/en/ARCHITECTURE.md   docs/pt-BR/ARCHITECTURE.md
docs/en/API.md            docs/pt-BR/API.md
docs/en/OPERATIONS.md     docs/pt-BR/OPERATIONS.md
docs/en/SECURITY.md       docs/pt-BR/SECURITY.md
```

### The case matrix, as counts

| What had to happen | Measured |
|---|---|
| documents produced that are in the map | 13 of 13 |
| documents produced that are **not** in the map | 0 |
| slots not earned, declared `not applicable` with a reason in the README index | 4 of 4 (ADR, agents, contributing, reports) |
| mirror present for every source document | 6 of 6 |
| `##` section count, source against mirror | equal in 6 of 6 |
| loose `.md` at the root beyond the canonical set | 0 |
| documents carrying the environment-variable header row | 2 — `docs/en/SETUP.md`, `docs/pt-BR/SETUP.md` |
| documents carrying the endpoint header row | 2 — `docs/en/API.md`, `docs/pt-BR/API.md` |
| layout audit of the result (`check-doc-layout.py`, L1-L7) | `findings: 0` |

The requirements document is the slot the fleet had zero of. The session produced nine functional
requirements read out of the code, not out of the old README — `FR-2` is the extension allowlist,
`FR-6` the fixed 320 kbps MP3 output, `FR-9` the health endpoint answering `503` when the `ffmpeg`
binary is missing from `PATH`.

The session also reported its migration as `old → new` per section, and named three claims in the
old documentation that the code contradicts.

### The defect this cell found, which nothing else could have

The first audit of the result was **not** clean:

```text
README.pt-BR.md:40: [L7] this table is owned by README.md; everywhere else links to it
```

That is a false positive, and a real one: the root mirror **is** the README in another language, so
it legitimately carries the README's own command table. L7 compared file names, and
`README.pt-BR.md` is not `README.md`.

The self-test could not have caught it. Its mirrors live in `docs/<tree>/`, where the twin's file
name is already identical; only the two root documents carry a language suffix, and only a real run
produces one. The fix folds the language tag before comparing owners, and the clean layout of the
self-test gained a root mirror carrying its owner's table so the case cannot regress. After it, the
same repository audits `findings: 0`.

This is the third time this catalog records the same lesson, and the first time for this skill: a
green self-test and a clean fleet run still shipped a defect that only an end-to-end run surfaced.

## Cell 2 — `repo-openspec`, a service that runs a spec-driven workflow

Source: `tools/talk-to-me`, which carries `openspec/specs/` with three capabilities and a legacy
layout: `README.md` in Portuguese, plus `docs/SETUP.md`, `docs/TECHNICAL.md` and
`docs/INTEGRATION.md`.

### The first attempt measured the harness, not the skill

**Observed**: 31 turns, 277 seconds, US$ 2.19, **zero files written**. The session read the whole
repository and stopped, because the maintainer's global rules — in context for every session,
headless included — forbid editing before the work is a backlog item, and treat a repository
carrying `openspec/` with no stated policy as requiring a change. Its words:

```text
Bloqueio do rito (decisão tua)
- Repo carrega `openspec/` e nenhuma config `spec_rite` (grep vazio) -> pelo teu rito,
  fail-closed: o item viraria também uma change OpenSpec.
- Sem `git remote` -> `/backlog` não tem onde criar issue.
- Ou me dás o waiver explícito ("docs-only, segue"), ou o número da issue onde isso cai.
```

That is the rite working, in a repository where it had nothing to protect. The re-run carried the
waiver in the prompt.

### The re-run

**Observed**: 89 turns, 1029 seconds, US$ 7.47 — against an estimate of about US$ 2, which is the
overrun this file's spend section reports. Its closing report opens:

```text
Documentação pronta.
## Migrações (`old → new`)
| `README.md` (português) | `README.pt-BR.md` |
| — | `README.md` (inglês, fonte) |
| `docs/SETUP.md` | `docs/pt-BR/SETUP.md` + `docs/en/SETUP.md` |
| `docs/TECHNICAL.md` | `docs/pt-BR/ARCHITECTURE.md` + `docs/en/ARCHITECTURE.md` |
| `docs/INTEGRATION.md` | `docs/pt-BR/INTEGRATION.md` + `docs/en/INTEGRATION.md` |
```

### The case matrix, as counts

| What had to happen | Measured |
|---|---|
| documents after | 24, in two trees |
| legacy documents migrated, not duplicated | 4 of 4 (no canonical document was created beside a legacy one) |
| `docs/TECHNICAL.md` renamed to the canonical name | yes, in both trees |
| requirements indexing the specifications instead of copying them | 3 capabilities, 3 links, 0 requirements copied |
| decisions extracted into ADRs | 4, mirrored 4 of 4 |
| slots not earned, declared with a reason | 4 (changelog, contributing, reports, agents) |
| pages outside the map | 1 (`INTEGRATION.md`), declared in the index with its reason |
| layout audit of the result (L1-L7) | `findings: 0` |

The requirements document is the property this cell existed to test:

```markdown
| Capability | Specification | Covers |
|---|---|---|
| `speak-api` | [openspec/specs/speak-api/spec.md](../../openspec/specs/speak-api/spec.md) | `POST /speak`, payload validation, bearer auth |
```

### What escaped

- **The map had no rule for a page it does not name.** The session kept `INTEGRATION.md`, put it in
  both trees, and declared it in the index with its reason: "not a slot of the standard map, kept
  because the caller's author is a distinct reader". That judgement is right, and the skill did not
  say so. It does now, as one paragraph: a page outside the map is declared in the index, owns no
  fact another slot owns, and is never unlisted. The checker does not verify it — which is why the
  rule is written as doctrine rather than counted as a gate.
- **The migration used `mv`, not `git mv`**, because `git mv` asked for an approval the headless
  session could not grant. The move is the same; the rename history is not. Worth knowing before
  running a migration this way at scale.
- **The session found five defects in the code it was documenting** — a dead config variable whose
  documented behaviour the code does not implement, a first deploy that comes up with authentication
  disabled, unauthenticated `/docs`, an unbounded queue, and a token comparison. None of that is
  measured here; it is recorded because "the documentation found the bug" is the argument for
  reading the code first, and this is the first time it happened in front of the rite.

## Spend

| Cell | Cost |
|---|---|
| `repo-plain` | US$ 4.83 |
| `repo-openspec`, blocked, no data | US$ 2.19 |
| `repo-openspec`, re-run with the waiver | US$ 7.47 |
| **Total** | **US$ 14.49** |

The ceiling fixed in [`protocol.md`](protocol.md) before the first cell was **US$ 5 for both runs**.
It was exceeded twice over, and each overrun is a separate failure of estimation worth naming:

1. The first cell alone spent US$ 4.83 against an estimate of about US$ 2. At that point the
   protocol's rule was applied: the blocked cell was **not** re-run, and the gap was reported.
2. The maintainer was then asked whether to spend about US$ 2 to close the gap and said yes. That
   cell cost **US$ 7.47** — nearly four times the figure the decision was made on.

The pattern behind both: a documentation run on a real repository writes 13 to 24 files, reads the
whole codebase first, and costs between US$ 5 and US$ 8 on this model. Any future measurement of
this skill should budget from that number, not from the per-cell figures this catalog has for
one-shot prompt benchmarks. The ceiling was never silently raised; it was broken, once by
underestimation and once by a decision taken on a bad estimate, and both are written here.

## Verdict

Read by the letter of [`protocol.md`](protocol.md): **SHIP.**

- Both cells produced a layout inside the map: 13 files from nothing, 24 files from a legacy layout
  migrated rather than duplicated. Both audit `findings: 0`.
- The two properties cell 2 existed to test are measured: requirements indexing the specifications
  (3 capabilities, 3 links, nothing copied), and legacy documents migrated in place (4 of 4, no
  canonical document created beside a legacy one).
- The REWRITE condition was not met. The one thing the map did not describe — a page outside its
  slots — the session declared instead of hiding, and the skill now carries that rule.
- The cost overrun is real, is double, and is reported rather than absorbed. It is a fact about this
  measurement's budgeting, not about the change.
