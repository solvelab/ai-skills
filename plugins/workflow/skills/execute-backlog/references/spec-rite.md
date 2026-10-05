# Spec rite — the gate between the item and the first edit

Applies only to a repo that runs a spec-driven workflow — the target repo, or each affected repo
from a workspace root, detected as below. No such repo → this file does not apply, and step 5 is a
no-op.

The workflow's own lifecycle — proposal format, delta format, when a proposal is required in the
vanilla doctrine — is **not** restated here. It lives in `openspec`, or in the project's fork
(`openspec-drivezone` is one). This file covers only the gate: what has to exist before a file is
edited, who decides, and what is written down.

## Detect the rite before deciding anything

Detect it where it lives for the repository the work targets, never in the cwd alone. In repo mode
the workflow is the nearest `openspec/` from the cwd up to the git root, inclusive — the CLI's own
resolution, stopped at the repository — so a subdirectory never hides it. From a workspace root it
is `<repo>/openspec`, once per affected repository. The CLI takes no path option, so every
`openspec` command in this file runs from that directory, the `<workflow-dir>` the detection prints:
run from a workspace root, a bare `openspec list` answers `No active changes found.`, which reads as
"no workflow", and `openspec validate <id>` answers `Unknown item '<id>'.`

```bash
# repo mode: from the cwd up to the git root, inclusive; the nearest openspec/ is the workflow
dir=""; if root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  root="$(cd "$root" && pwd -P)"; dir="$(pwd -P)"   # both through this shell: Git Bash C:/ vs /c/
  until [ -d "$dir/openspec" ] || [ "$dir" = "$root" ] || [ "$dir" = / ]
  do dir="$(dirname "$dir")"; done
else echo 'not inside a repository: workspace mode sets dir="$PWD/<repo>" once per affected repo'
fi
# workspace mode: no walk; once per affected repo, dir="$PWD/<repo>" (that repo's root only)
if [ -z "$dir" ]; then :                            # outside a repository nothing is detected here
elif [ -d "$dir/openspec" ]; then
  echo "workflow-dir: $dir"                         # where every openspec command runs from
  grep -m1 '^schema:' "$dir/openspec/config.yaml"   # which schema it runs; absent → vanilla
  (cd "$dir" && openspec list)                      # an open change may already cover the work
else echo "no spec-driven workflow in this repo"; fi
```

A forked schema changes the artifacts, not the gate. Read the fork's own skill when one exists, and
scaffold with it so the mandatory sections come from the repo's template:

```bash
(cd <workflow-dir> && openspec new change <change-id> --schema <schema-name>)
```

`openspec templates` resolves the **default** schema, not the one in `openspec/config.yaml` — pass
`--schema` explicitly or you get vanilla templates in a forked repo. Probed on CLI 1.6.0.

## The verdict is inherited, re-checked, and never re-decided quietly

The item created by `backlog` already carries a verdict: the change that will exist, or a written
waiver and its reason. Re-check it against the surface the context re-analysis just measured. From a
workspace root the item carries one verdict per affected repo that runs the workflow; each is
re-checked on its own, and its change is created and validated in that repo.

| Situation | Move |
|---|---|
| Item says a change is required | Create it, validate strict, carry the id into the plan |
| Item waived it, and re-analysis agrees | Proceed; the waiver line goes in the PR body verbatim |
| Item waived it, and the work turned out bigger | **Raise it without asking.** Create the change, say so in the plan |
| Item requires it, and it now looks unnecessary | **Stop and ask.** Only the user lowers a verdict |
| Item carries no verdict (groomed before the rite, or another tool) | Treat the repo policy as the verdict; `required` when the repo states none |

The asymmetry is deliberate. A silent downgrade is the failure this gate exists to prevent: it is
what shipped two blocking CI gates with no proposal and forced a retroactive change to register
them afterwards. Raising a verdict costs an artifact nobody objects to; lowering one costs the trail.

## Policy comes from the repo, not from this skill

`spec_rite` in the backlog config, read for the repo the work targets — from a workspace root, for
each affected repo. Which file answers for a repo — file by file in repo mode, key by key from a
workspace root — is written once in the `backlog` skill: the file
`skills/backlog/references/backlog-config.md`, *Precedence*.

```yaml
spec_rite:
  tool: openspec        # which workflow; read from openspec/config.yaml when present
  policy: required      # required | triage | none
```

- `required` — every code-producing item carries a change; the only exit is the written waiver.
- `triage` — the workflow's own doctrine decides (`openspec`, *When a proposal is required*).
- `none` — the repo has the workflow but does not gate on it.

Key absent wherever that precedence reads it while the workflow is present → treat as `required`.
An unstated policy is the absence of a decision, not permission to skip.

## Before the first edit outside the workflow's directory

```bash
# the gate, not a formality — fix until green
(cd <workflow-dir> && openspec validate <change-id> --strict)
```

Green is the precondition for step 6. The plan presented for approval carries the change id, the
capabilities its delta touches, and this command's output line, so the approver sees what was
registered before approving what will be built.

## During implementation

Tick the change's task list task by task, as each one lands and is validated — not in a batch at the
end. A batch tick at the end records intent, and intent is what the rite is trying to stop.

## In the PR body

The line the repo's gate reads, one of:

```text
Spec-rite: <change-id>
Spec-rite: none — <the reason the work registers nothing>
```

A waiver with no reason is worse than no waiver: it looks decided and says nothing.

A repo that also gates each skill's `metadata.version` (this catalog does, with
`scripts/validate-skill-version.py`) reads a second line from the same body when the diff edits a
skill without moving its version: `Skill-version: none — <the reason these edits deserve no bump>`.
One line covers every skill in the PR; the reason has the same minimum length as the `Spec-rite`
waiver; a version that goes **down** is never waived. The default is to bump — the line exists for
the sweep that adds one cross-reference to twelve skills, not for the PR that changes what one of
them does.

## Archive is not part of this run

`openspec archive` syncs the delta into the main specs. Doing it in the implementation PR would move
the specs before a human approved the code they describe. Leave the change **active**, and report it
as pending in the final summary, naming the follow-up that closes it. Repos that separate the two
carry the precedent in their history — look for an archive-only commit or PR before assuming
otherwise.
