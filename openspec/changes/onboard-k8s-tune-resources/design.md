## Context

`k8s-tune-resources` shipped to every Claude Code user of this repo while sitting outside every
control the catalog has. It was found by cross-checking the wrapper trees against the canonical one
during a catalog-wide audit — not by any gate, because no gate looked there.

It is also the most destructive skill in the catalog: it clones a fleet of repositories, rewrites
their chart values with `sed`, commits and pushes. A real run touched 51 repositories.

## Goals / Non-Goals

**Goals**
- Bring the skill under the same rules as every other one.
- Give an operation of this blast radius a dry run and a rollback path.
- Make the orphan state impossible to reach again silently.

**Non-Goals**
- Not rewriting the skill's approach. The discovery-from-pod-images workflow is sound and stays.
- Not rewriting git history to purge the values already published. That is the repository owner's
  decision; this change stops the leak going forward and says so.
- Not generalising the skill beyond Bitbucket/SSH. The clone template is called out as an assumption
  instead.

## Decisions

**D1 — Promote, do not delete.** The skill does real work and its workflow is battle-tested at 51
repos. Deleting it would lose that; leaving it orphaned would keep it unchecked. Promotion is the only
option that ends with it governed.

**D2 — `DRY_RUN=1` is the default, not a documented option.** The previous safety was a sentence
asking the operator to confirm scope. For an operation with no undo, the guard has to be in the code
path: the loop now stops after staging and reports `WOULD_CHANGE` with a diffstat unless `DRY_RUN=0`
is passed deliberately.

**D3 — Rollback is written before the run, not after.** Every repo lands exactly one commit, so a
`git revert HEAD` per repo is sufficient and safe on shared branches. The skill says to prepare it up
front, and forbids fleet-wide force-pushing.

**D4 — Operational values are inputs, never doctrine.** Cluster addresses, org slugs and app-name
prefixes belong to a run. The skill already collects them in *Required inputs*; recording them a
second time as "memorized facts" gained nothing and published internal detail from a public repo. The
blast-radius figure is kept because the *number* is the lesson; the addresses are not.

**D5 — The catalog requirement becomes structural, not numeric.** The existing requirement asserted
"exactly 20 skills" and had been wrong for some time — the catalog is at 31. A count in a spec is a
guaranteed future falsehood; the rule that matters is that the canonical tree defines the set.

**D6 — C7 checks generated trees, not just the canonical one.** The whole failure was that every check
looked only where the file was not. The new check inverts the direction: walk the generated trees and
demand a source for each entry.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Bulk resource tuning across repos discovered from a cluster | `k8s-tune-resources` | establish here (promoted from an orphan wrapper) |
| Kubernetes YAML → Helm chart conversion | `helm-migration` | unchanged; different job, no overlap |
| Commit message format for the commits this skill creates | `conventional-commit` | link (already canonical) |
| What the catalog is, and how a skill is added | `openspec/specs/skills-catalog` | spec delta |
| Mechanical enforcement of authoring rules | `scripts/validate-skills.py` | already canonical — gains C7 |

## Risks / Trade-offs

- [`DRY_RUN` defaulting to 1 breaks anyone who copy-pasted the old loop into automation] → intended;
  the failure mode is "nothing was pushed", which is the safe direction, and the report says why.
- [Promoting the skill makes an org-specific workflow more visible] → the org-specific values are
  removed and the remaining workflow is generic; it was already public.
- [C7 only walks `claude/` and `codex/`] → those are the two trees that install as skills; `cursor/`
  and `copilot/` emit flat files, and `plugins/` is assembled from the canonical set by `generate.sh`.
- [Removed values persist in git history] → stated in the proposal as out of scope and left to the
  repository owner.
