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
- [Cell 2 — blocked before the skill ran](#cell-2--repo-openspec-blocked-before-the-skill-ran)
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

## Cell 2 — `repo-openspec`, blocked before the skill ran

Source: `tools/talk-to-me`, which carries `openspec/specs/` with three capabilities and a legacy
documentation layout (`docs/SETUP.md`, `docs/TECHNICAL.md`, `docs/INTEGRATION.md`).

**Observed**: 31 turns, 277 seconds, US$ 2.19, **zero files written**. The session read the whole
repository and then stopped, because the maintainer's own global rules — which are in context for
every session, headless included — forbid editing before the work is a backlog item, and treat a
repository carrying `openspec/` with no stated policy as requiring a change. Its words:

```text
Bloqueio do rito (decisão tua)
- Repo carrega `openspec/` e nenhuma config `spec_rite` (grep vazio) -> pelo teu rito,
  fail-closed: o item viraria também uma change OpenSpec.
- Sem `git remote` -> `/backlog` não tem onde criar issue.
- Ou me dás o waiver explícito ("docs-only, segue"), ou o número da issue onde isso cai.
```

**This cell produced no measurement of the skill**, and it is reported as blocked rather than as a
result. What it does measure is the harness: documenting a repository is a code change under the
maintainer's rite, so a headless documentation run in a spec-driven repository needs the waiver in
its prompt. The re-run needs one sentence added to the prompt and would cost about US$ 2.

Two properties therefore remain **unmeasured end to end**, and they are the ones this cell existed
to test:

- that `REQUIREMENTS.md` indexes `openspec/specs/` instead of copying it;
- that a legacy layout is migrated rather than duplicated.

Both are covered by the detector's own rules (L2 names every legacy document and its destination)
and by the skill's text, and neither has been watched happening in a live session.

## Spend

| Cell | Cost |
|---|---|
| `repo-plain` | US$ 4.83 |
| `repo-openspec` (blocked, no data) | US$ 2.19 |
| **Total** | **US$ 7.02** |

The ceiling fixed in [`protocol.md`](protocol.md) before the first cell was **US$ 5 for both runs**,
and it was exceeded: the first cell alone spent US$ 4.83, against an estimate of roughly US$ 2. The
ceiling was **not raised** — the second cell was not re-run, which is why cell 2 is reported as
blocked rather than retried. Recording the overrun is the point: a ceiling that is quietly raised
the first time it binds is not a ceiling.

## Verdict

Read by the letter of [`protocol.md`](protocol.md): **SHIP, with one arm unmeasured.**

- Cell 1 produced a layout entirely inside the map, with the mirror pair complete, ownership held,
  every unearned slot declared, and a clean audit. That is the SHIP condition for the arm that ran.
- Cell 2 is blocked, not failed. The REWRITE condition — "a simulation run produces a layout the map
  does not describe" — was not met, because no layout was produced at all.
- The cost overrun is a fact about this measurement's budgeting, not about the change. It is
  reported here and in the pull request rather than absorbed.
