# Results

Measured on **2026-09-12** by the maintainer's session, against a private workspace of 39 git
repositories. Every command below was run; every count is the raw output of one of them. The
thresholds and the verdict these numbers are read against were fixed first, in
[`protocol.md`](protocol.md), which restates what the change's `design.md` carried at commit
`59dc13c` — before the detector existed and before any repository was scanned.

## Pass 1 — inventory

```bash
find . -maxdepth 3 -type d -name .git | xargs -n1 dirname | sort | while read -r r; do
  find "$r" -maxdepth 2 -iname '*.md' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.venv/*' \
    -not -path '*/.pytest_cache/*' -not -path '*/openspec/*' -not -path '*/.claude/*' \
    -not -path '*/.cursor/*'
done | awk -F/ '{print $NF}' | sort | uniq -c | sort -rn
```

39 repositories, 18 of them running a spec-driven workflow.

| Concept | Spellings found, with counts |
|---|---|
| entry | `README.md` 55 |
| history | `CHANGELOG.md` 33 |
| tutorial | `SETUP.md` 21 · `COMO-SUBIR.md` 1 |
| explanation | `TECHNICAL.md` 19 · `ARCHITECTURE.md` 12 · `DESIGN.md` 1 |
| agents | `CLAUDE.md` 18 · `AGENTS.md` 13 |
| api | `API.md` 9 · `api-contract.md` 1 · `endpoints.md` 1 |
| operation | `DEPLOYMENT.md` 6 · `INFRASTRUCTURE.md` 4 · `RUNBOOK.md` 2 · `DEPLOYMENT_GUIDE.md` 2 · `DEPLOY.md` 1 |
| security | `SECURITY.md` 3 |
| **requirements** | **0** |

Three counts carry the argument for the map:

- **11 of 39 repositories carry two names for the explanation slot at once** — a root
  `ARCHITECTURE.md` beside a `docs/TECHNICAL.md`, in `fabcost3d-mqtt-agent`, `fabcost3d-shopee`,
  the six `filial-*` services, `filial-ml`, and both `speak-memo-*` repositories.
- **Six spellings for the operation slot**, none of which covers the whole slot. `DEPLOYMENT.md`,
  the most common, names only how the software goes out; what it needs to run and what to do when
  it breaks went to `INFRASTRUCTURE.md` and `RUNBOOK.md`.
- **Zero requirements documents and zero ADR directories**, in 39 repositories:

  ```bash
  find . -maxdepth 4 \( -iname 'REQUIREMENTS.md' -o -iname 'REQUISITOS.md' \
       -o -type d -iname adr -o -type d -iname adrs \) | wc -l
  # 0
  ```

The same name is also not the same document. Across the 19 `docs/TECHNICAL.md`:

```bash
find . -maxdepth 4 -path '*/docs/TECHNICAL.md' | while read -r f; do
  printf "%3d  %s\n" "$(grep -cE '^## ' "$f")" "$f"
done
```

| Sections `##` | Repository |
|---|---|
| 7 | `tools/ai-commit-messages` |
| 9 | `fabcost3d/fabcost3d-mqtt-agent` |
| 11 | `observability/feldt`, `editaudiotomovie/whisper`, `fabcost3d/fabcost3d-notification-hub`, `fabcost3d/fabcost3d-web-manager` |
| 12-15 | nine repositories |
| 22 | `observability/k8s-troubleshoot-bot` |
| 25 | `filial/filial-backend-rest-api` |

The skeleton that produced them prescribed ten sections, and the worked example beside it
demonstrated six. One name, nineteen shapes.

**Transient records sit outside any reports directory, and they sit in two different places.**
The survey counts what is inside a repository; a second count was needed for what is not:

| Where | Count | Command |
|---|---|---|
| inside a repository | 7 | `survey.py --root <workspace> --inventory` |
| loose in a workspace directory, outside every git repository | 17 | `find . -maxdepth 2 -iname '*.md' \| grep -icE 'HOMOLOG\|DIAGNOSE\|CORRECAO\|TESTE_AGORA\|ROTEIRO\|CONTINUAR'` |

The seven inside repositories are two validation reports at a root, two re-validation notes inside
`docs/`, a `PROGRESS.md`, a `TODO.md` and one evidence note. The seventeen outside are homologation
write-ups, a diagnosis and two Portuguese-named notes, in the `filial` and `fabcost3d` workspace
directories. Only the first group is a documentation-layout defect the skill can act on; the second
is what a workspace root collects when no document has a home, and it is the reason the map gives
dated records one.

The issue estimated "≥ 9" for this and put the fleet at "~25 repositories". Both were low: 39
repositories, and 24 transient records across the two locations.

Finally, **0 of 39 repositories declare `.code-locale`**, which is why the conflict between the
two-language pair and the prose detector is a predicted conflict rather than an observed one. That
gap is recorded in the change's evidence group, not resolved here.

## Pass 2 — detector, findings per rule

```bash
python3 research/documentation-layout/survey.py --root <workspace> --markdown
```

Ten repositories, chosen to cover both workflows and four different workspaces: `feldt`,
`ferdinand`, `k8s-troubleshoot-bot`, `filial-backend-rest-api`, `filial-amazon`,
`fabcost3d-mqtt-agent`, `fabcost3d-backend-rest-api`, `talk-to-me`, `speak-memo-backend`,
`kokoro-tts-server`.

| Rule | Findings | Confirmed by hand | False positives | Verdict |
|---|---|---|---|---|
| L1 | 13 | 13 | 0 | with validator |
| L2 | 38 | 38 | 0 | with validator |
| L3 | 3 | 2 | 1 | with validator |
| L4 | 4 | 4 | 0 | with validator |
| L5 | 5 | 5 | 0 | with validator, delegated |
| L6 | 0 | — | — | with validator, proved by self-test only |
| L7 | 1 | 1 | 0 | with validator |
| **Total** | **64** | **63** | **1** | — |

Every finding was opened and read against its repository, one at a time, on 2026-09-12. What each
rule found:

- **L1 (13).** Ten repositories with no requirements document at all; three with no `## Documentation`
  index in the README. Confirmed against the file system and, for the index, against the README's
  own heading list — `feldt` and `filial-backend-rest-api` do carry `## Documentação`, and the rule
  correctly stayed silent on both, which is the accent-folding path working.
- **L2 (38).** Legacy names and canonical names outside their tree. This is the highest-volume rule
  and it is measuring a migration, not a defect rate: it goes quiet once the fleet moves.
- **L3 (3), one false positive.** Two confirmed: `README-fork.md`, a second entry document, and
  `CICD_SETUP.md`, a tier document left at the root. The false positive is `NOTICE-fork.md`, a
  provenance notice in a repository that forks an upstream project — a variant of `NOTICE.md`, which
  the allowlist accepts under its own name. Fork-provenance files are what `--exclude` is for.
- **L4 (4).** Two validation reports at a repository root and two re-validation notes inside
  `docs/`. All four are records of one moment.
- **L5 (5).** Three Portuguese file names in one repository's spike and script directories, and two
  re-validation notes in another. All five are verdicts from the delegated checker, not its advisory
  tier.
- **L6 (0).** Not one of the ten repositories documents in two trees, so the rule had nothing to
  find. It is proved by its two injected defects — a missing twin, and a mirror whose code block was
  translated — and by nothing else. Saying so is the difference between a measurement and a claim.
- **L7 (1).** `k8s-troubleshoot-bot` carries an identical six-row `| Comando | O que faz |` table in
  `README.md:103` and `docs/SETUP.md:58`. The copies still agree. That is exactly the state the rule
  exists to catch: they agree until one of them is edited, and nothing signals which one that was.

### One false positive that is not in the table

An earlier run over five of these repositories reported a root `CLAUDE.md` as a loose document.
That is wrong — an agent-instruction file at the root is a class the skill itself names. The root
allowlist gained `CLAUDE.md`, `GEMINI.md` and GitHub's community-health files, and the run in the
table above is the one taken after that fix.

It is recorded here rather than dropped because a measurement that reports only the findings the
tool survived measures the tool's confidence, not its accuracy.

### Four defects the detector's own self-test caught before any repository saw it

All four were found by `check-doc-layout.py --selftest`, which injects one defect per rule and
asserts a clean layout stays silent:

1. Folding the whole file stem before splitting turned `README.pt-BR` into one unrecognizable word,
   so a correct mirrored README at the root was reported as loose.
2. The "declared absent" check searched the whole index section instead of one line, so an index
   that declared any slot absent satisfied the rule for every slot.
3. The injected defect for L5 (`COMO-SUBIR.md`) produces only an advisory in the delegated checker,
   so the case proved nothing; it was replaced with a name that produces a verdict.
4. The L6 message computed its count with an expression whose `or 1` branch was unreachable.

## Pass 3 — simulation

The measurement that a green self-test cannot replace: what a real session leaves behind when it
runs the changed skill.

Both repositories were copied to a throwaway directory, stripped of their git history and
re-initialized, and the changed skill was installed project-scoped at
`.claude/skills/documentation/` — the layout `generate.sh` publishes into `claude/skills/`. The
session was then asked, in the words a user would use, to document the repository.

```bash
claude -p "Documente este repositório. Siga a skill documentation." \
  --permission-mode acceptEdits --output-format json
```

| | `repo-plain` (no spec workflow) | `repo-openspec` (3 capabilities) |
|---|---|---|
| Source | `editaudiotomovie/combine-audio` | `tools/talk-to-me` |
| Documents before | `README.md`, `CHANGELOG.md` | `README.md`, `docs/SETUP.md`, `docs/TECHNICAL.md`, `docs/INTEGRATION.md` |

The observed outcome of each run, the files that appeared, and the detector's verdict on the result
are recorded in [`simulation.md`](simulation.md), together with the cost against the US$ 5 ceiling
the protocol fixed in advance.

## Verdict

Read by the letter of [`protocol.md`](protocol.md):

- **Every rule is far below the noise level that sends a rule to review-only.** The worst is L3 at
  1 false positive in 3 findings; the level this catalog already rejected is 7 in 10, and L3's one
  miss is a scope question with an existing exit (`--exclude`), not an accuracy one. One rule, L6,
  has no fleet evidence at all and ships with that stated rather than implied.
- The inventory confirms the problem the map exists to solve, at a size larger than the issue
  estimated: the item said "~25 repositories", the fleet has 39, and the transient records it put
  at "≥ 9" are 24 across the two locations counted above.

The simulation arm decides the rest, and its verdict is written in [`simulation.md`](simulation.md).
