# Tasks: add-execute-backlog-skill

## 1. Skill authoring

- [x] 1.1 `skills/execute-backlog/SKILL.md` — frontmatter (category process, English); flow:
      locate issue → completeness gate → context re-analysis → implementation plan → approval gate
      → branch-per-item → implement → tests → validation discovery/run → fix findings → PR(s) with
      `Closes #n` on primary → board sync → summary; safety rails (no merge, no direct close, no
      default-branch work, scope-change protocol).
- [x] 1.2 `references/execution-flow.md` — plan format, completeness checklist, scope-change
      protocol, multi-repo orchestration (clone check, per-repo PRs).
- [x] 1.3 `references/validation-matrix.md` — discovering test/lint/build/typecheck per stack from
      manifests (package.json, pyproject, Makefile, fxmanifest, etc.); run-what-exists rule.
- [x] 1.4 `references/board-sync.md` — status transitions (in-progress on start, review on PR),
      runtime ID resolution, PR↔issue linking, recovery commands.

## 2. Wrappers & catalog integrity

- [x] 2.1 `./generate.sh`; wrappers present in all five outputs; README table + count updated.
- [x] 2.2 Local CI parity: frontmatter checks + clean regeneration diff.

## 3. Tests & validation (controlled)

- [x] 3.1 Locate gate: `/execute-backlog` with nonexistent number → clear error, nothing touched.
- [ ] 3.2 Completeness gate: issue without acceptance criteria → gaps reported, user asked, no code
      changed.
- [ ] 3.3 Controlled run on a real test issue: plan presented and approved → implementation on a
      new branch → repo validations executed → PR opened with `Closes #n` → board item moved to
      review column; evidence collected (PR URL, checks output, item-list JSON).
- [ ] 3.4 Safety: confirm no commit lands on the default branch and the issue is not closed by the
      skill itself.

## 4. Closure

- [ ] 4.1 README entry present; archive change after user validation.
- [ ] 4.2 Present evidence to the user.
