# Change: Bring k8s-tune-resources into the catalog, and stop orphan skills recurring

## Why

`k8s-tune-resources` existed only as `claude/skills/k8s-tune-resources/SKILL.md` — 133 lines of real
content in a **generated** tree, with no `skills/k8s-tune-resources/` source behind it. Everything
that governs a catalog skill therefore skipped it:

- `generate.sh` never produced its `codex/`, `cursor/`, `copilot/` or `plugins/` variants
- the CI frontmatter check globs `skills/*/SKILL.md`, so its missing `license` and `compatibility`
  were never caught, and its `metadata.author: diegops` never reconciled with the catalog's `solvelab`
- `scripts/validate-skills.py` never checked it — the catalog reported 30 skills; there were 31
- the README never listed it, so nobody browsing the catalog knew it shipped

It was still installed for every Claude Code user of this repo.

Reviewing it surfaced three further problems:

1. **It published internal infrastructure to a public repo.** A "Memorized facts" section carried two
   cluster node addresses (RFC1918), a customer org slug and an application-name prefix. No
   credentials, so the severity is low — but the skill works without any of it, and the run already
   asks for those values as inputs.
2. **No dry run.** Step 2 clones, patches, commits *and pushes* in one loop. Its only guard was a
   prose line saying to confirm scope first. A real run pushed to **51 repositories**.
3. **No rollback path**, for an operation whose blast radius is 51 shared branches.

## What Changes

- `skills/k8s-tune-resources/SKILL.md` created (2.0.0) from the orphan, with catalog-conformant
  frontmatter (`solvelab`, MIT, `compatibility`, folded description), and the orphan
  `claude/skills/k8s-tune-resources/` deleted so `generate.sh` owns every tree.
- **`DRY_RUN` wired into the loop, defaulting to `1`** — it clones, patches and reports
  `WOULD_CHANGE` with a diffstat, and never pushes until explicitly set to `0`. Verified with
  `bash -n` after substituting the placeholders.
- **Rollback documented before the push**: the per-repo `git revert` command, and the rule to revert
  rather than force-push across a fleet.
- **Blast radius stated**: 51 repositories from one label selector, with the two commands that size a
  run before you make it.
- Cluster addresses, customer org and app-name prefixes removed; the required-inputs list already
  collects them per run. A standing instruction not to record them here was added.
- **Verified against** `kubectl v1.36.1` and `git 2.47.3` — every flag the workflow uses (`-l`, `-A`,
  `--field-selector`, `-o jsonpath`) probed against that client.
- New validator check **C7 — no orphan wrapper skills**: every directory under a generated tree must
  have a canonical `skills/<name>/SKILL.md`. Self-test extended to 11 defect classes.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-catalog`: MODIFIED **Catalog composition after the quality review** — the catalog is the set
  of `skills/*/SKILL.md`; a skill present only in a generated tree is not a catalog skill and is
  rejected by CI.

## Impact

- New `skills/k8s-tune-resources/SKILL.md`; `claude/skills/k8s-tune-resources/` replaced by the
  generated wrapper; new `codex/`, `cursor/`, `copilot/`, `plugins/devops/` variants.
- `scripts/validate-skills.py` (+C7), `scripts/selftest-validate-skills.py` (11 classes), README row.
- Catalog count goes 30 → 31.
- **Not done here:** the removed values remain in git history. Rewriting published history is the
  repository owner's call, not this change's.
