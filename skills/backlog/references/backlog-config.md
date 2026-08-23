# Config schema

Two files, same schema. Field *names* only — IDs are resolved at runtime, never persisted.

| Mode | File | When |
|---|---|---|
| Repo | `.github/backlog.yml` (repo root) | cwd is inside a git repository |
| Workspace | `backlog.yml` (workspace root) | cwd is a directory whose subdirectories are git repos of one org |

**Precedence**: inside a repo, the repo's own `.github/backlog.yml` wins; if absent, inherit the
workspace `backlog.yml` from the parent directory (if any). Commit the file — teammates inherit the
setup on clone; it contains no secrets (auth is each user's own `gh` login).

## Repo mode example

```yaml
version: 1
project:
  owner: my-org        # org or user that owns the Project v2
  number: 1            # gh project list --owner my-org
# repo: my-org/my-repo # optional override; default = origin remote
fields:                # Project field names as shown by gh project field-list
  status: Status
  priority: Priority
  size: Size
  estimate: Estimate
defaults:
  status: Backlog      # column for newly created items

# Optional — read by `execute-backlog` when it advances the card. Absent keys fall back to
# name heuristics; a name that is not among the board's Status options is warned about and
# skipped, never fatal. Canonical definition: execute-backlog/references/board-sync.md
columns:
  ready: Ready
  in_progress: In progress
  review: In review
labels:                # optional: intent → existing repo label
  feature: enhancement
  bug: bug
assignees: []          # optional default assignees (GitHub logins)

# Optional — the repo's spec-driven policy. See "Spec rite" below.
spec_rite:
  tool: openspec
  policy: required
```

## Workspace mode example

```yaml
version: 1
project:
  owner: my-org
  number: 1
workspace:
  # repos: [api, worker, web]   # optional allowlist; default = every child dir with .git
  # issues_repo: my-org/planning # optional: force all issues into one repo;
                                 # default = primary affected repo per item
fields:
  status: Status
  priority: Priority
  size: Size
  estimate: Estimate
defaults:
  status: Backlog
```

## Spec rite (`spec_rite`)

The policy belongs to the repository, not to this skill: both backlog skills run against
repositories with different rites, so hardcoding one here would export a single project's process to
every project.

```yaml
spec_rite:
  tool: openspec        # which spec-driven workflow; read from openspec/config.yaml when present
  policy: required      # required | triage | none
```

| `policy` | Meaning |
|---|---|
| `required` | Every code-producing item declares a change; the only exit is a written waiver with a reason |
| `triage` | The workflow's own doctrine decides — `openspec`, *When a proposal is required* |
| `none` | The repository carries the workflow but does not gate on it |

**Key absent while the workflow is present ⇒ `required`.** An unstated policy is the absence of a
decision, not permission to skip. No workflow present ⇒ the whole gate is a no-op and the drafted
item carries no spec section.

The verdict this key produces is consumed by `execute-backlog`
(`execute-backlog/references/spec-rite.md`), which re-checks it and may raise it.

## Mirroring an item onto a second board (`extra_projects`)

A repository can be relevant to more than one Project: a website repo whose game page is tracked on
that game's board, a shared library tracked by each consuming squad. An issue may belong to several
Projects at once, so the item is **added** to each — never moved.

```yaml
project:                 # the primary board — owns field values and the lifecycle
  owner: solvelab
  number: 2
extra_projects:          # optional mirrors, in addition to the primary
  - owner: DriveZoneFivem
    number: 1
    # status: Backlog    # optional; default = the primary's defaults.status
```

Rules:

- The primary Project stays the source of truth: `fields:`, `defaults:` and `columns:` describe it.
- On each mirror the skills set **Status only**, using the option whose *name* matches (option IDs
  are per-board and must be resolved fresh for each one — two boards cloned from the same template
  can even share option IDs, which makes copying them look like it works right up until it doesn't).
- Priority/Size/Estimate are left untouched on mirrors. An org **issue field** (Priority in a
  solvelab board, say) cannot be set from another org's Project anyway.
- A mirror that fails — board gone, no Status field, no matching option — produces a warning and is
  skipped. It never fails the run and never blocks the primary board.
- Cards on different boards drift: whoever moves one by hand should move the other. The skills only
  sync the transitions they perform themselves.

## Validation rules

- `project.owner` and `project.number` are required; anything else is optional.
- Each entry in `extra_projects` requires `owner` and `number`; `status` is optional.
- Unknown keys: warn and ignore (forward compatibility).
- A `fields:` entry naming a field that does not exist in the Project → warn + skip that field at
  creation time (do not fail the run).
- `defaults.status` must be one of the Status options returned by `gh project field-list`;
  otherwise warn and leave Status unset.
