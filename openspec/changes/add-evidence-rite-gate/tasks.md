## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion — a row a reviewer can re-run in two seconds is the only kind
     worth writing. A claim with no evidence is a guess: drop the claim, or go get the evidence.
     Doctrine: the verify-before-claiming skill. -->

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at. Read at `c965689` on 2026-08-06:
      `scripts/validate-rite.sh` (50 lines; the three existing greps are at lines 22, 24 and 35, and
      the last-group `case` at 26-30 is the idiom the new first-group check mirrors),
      `openspec/config.yaml` (its `context` block said "forces three gates"),
      `openspec/schemas/skills-rite/schema.yaml` (line 3 `description` and the `MANDATORY GATES`
      prose in the tasks instruction both said three), `openspec/schemas/skills-rite/templates/tasks.md`,
      `claude/global/hooks/backlog-rite.py` (the payload/SIGNALS/SKIP contract cloned here),
      `README.md:221-253` (the only hook wiring documented anywhere).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded.
      `bash --version` -> `GNU bash, version 5.2.37(1)-release`; `python3 --version` -> `Python
      3.14.5`; `openspec --version` -> `1.6.0`.
      `python3 -c "import json;print(list(json.load(open('.claude/settings.local.json')).keys()))"`
      -> `['permissions']`, which is the evidence for the README's claim that this repo ships hooks
      for consumers and does not self-apply them.
      `grep -c "claude/global" generate.sh` -> `0`, which is the evidence that no wrapper
      regeneration is needed for the hook.
      Hook behaviour probed by piping payloads on stdin: 24 correction phrases (pt-BR + English) all
      printed the reminder, 5 neutral technical prompts and 6 waiver phrases printed nothing, and
      `echo 'not json' | python3 claude/global/hooks/verify-rite.py` exited `0`.
      One defect was found and fixed by that probe rather than by review: `essa opção não existe`
      did not match, because the pattern assumed the demonstrative and the negation were adjacent.
- [x] E.3 Anything that could NOT be probed is written down as an open question — never stated as
      fact, never filled with a plausible substitute. Two items: whether a `PreToolUse` transcript
      proxy would detect un-researched edits at an acceptable false-positive rate was **not**
      measured, so the variant is documented in the hook docstring as rejected-on-grounds rather
      than as ineffective; and whether the correction-only trigger fires often enough in practice is
      not measurable before the hook ships, so no effectiveness claim is made for it anywhere.
- [x] E.4 Scope check: this change does only what the proposal asked. Noticed and **not** performed:
      the drifted skill counts in `README.md` and `.claude-plugin/marketplace.json`, and the stale
      category set in `openspec/specs/skills-authoring/spec.md` — all three belong to a sibling item
      and are listed here as follow-ups, not fixed in passing.

## 2. The fourth gate

- [x] 2.1 `scripts/validate-rite.sh` — grep for `Evidence & Sources (MANDATORY)` plus a first-group
      position check mirroring the existing last-group `case` on `Validation & Closure`
- [x] 2.2 `scripts/validate-rite.sh` — `KNOWN LIMIT` header stating it checks presence and position,
      never whether a ticked box was earned
- [x] 2.3 `openspec/schemas/skills-rite/templates/tasks.md` — prepend the group as `## 1.` and
      renumber the existing groups to 2 / 3 / 4
- [x] 2.4 `openspec/schemas/skills-rite/schema.yaml` — `description` and the `MANDATORY GATES` prose
      move from three gates to four, including the first-position constraint
- [x] 2.5 `openspec/config.yaml` — `context` says four gates and names the enforcing script;
      `rules.tasks` forbids a doctrine line whose evidence is not recorded
- [x] 2.6 Backfill the group into the in-flight `add-verify-before-claiming/tasks.md` so the gate
      does not break work already open

## 3. Runtime artifacts

- [x] 3.1 `claude/global/hooks/verify-rite.py` — correction-triggered `UserPromptSubmit` hook with
      the same informs-never-blocks contract as `backlog-rite.py`
- [x] 3.2 Hook docstring carries the `KNOWN LIMIT` and the rejected `PreToolUse` variant with its
      failure modes named
- [x] 3.3 `claude/global/personal-rules.md` — `## Grounding (no achismo)` block for the preventive,
      once-per-session coverage
- [x] 3.4 `README.md` — the combined wiring, what the hook does not cover, and the layer that
      enforces evidence when the hook is not wired

## 4. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Every skill added or edited
     by this change gets checked against the skills-authoring spec. Keep the group number
     as the second-to-last group. -->

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: no `skills/` file is touched by this
      change, so the requirement is vacuously satisfied and `validate-skills.py` still exits 0
- [x] Q.2 All touched content in English (catalog locale); pt-BR appears only as regex trigger
      literals inside the hook, which is the same precedent as `backlog-rite.py`
- [x] Q.3 Description triggers testable: no skill description changes; the hook's trigger list is
      exercised by the 35-case probe recorded in E.2
- [x] Q.4 No duplicated doctrine: the hook reminder and the `personal-rules.md` block carry a
      compressed operational form and name `verify-before-claiming` as the full doctrine, per the
      design.md Canonical Home table — no mechanism list is reproduced
- [x] Q.5 The gate was tested **negatively**, not only positively: a scratch change missing the
      group fails, a scratch change with the group out of position fails, and a well-formed change
      passes

## 5. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [x] V.1 `openspec validate add-evidence-rite-gate --strict` green
- [x] V.2 Catalog discovery intact: 33 skills, every `name` matching its directory, no orphan
      wrappers; `./generate.sh` leaves no diff
- [x] V.3 README / docs updated where the change alters usage
- [ ] V.4 `openspec archive add-evidence-rite-gate --yes` after all groups above are `[x]`
      — per this repo's established sequence this happens in a follow-up PR after the
      implementation PR merges (precedent: PR #61 shipped the active change, PR #62 archived it)
