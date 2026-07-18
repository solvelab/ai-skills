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
labels:                # optional: intent → existing repo label
  feature: enhancement
  bug: bug
assignees: []          # optional default assignees (GitHub logins)
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

## Validation rules

- `project.owner` and `project.number` are required; anything else is optional.
- Unknown keys: warn and ignore (forward compatibility).
- A `fields:` entry naming a field that does not exist in the Project → warn + skip that field at
  creation time (do not fail the run).
- `defaults.status` must be one of the Status options returned by `gh project field-list`;
  otherwise warn and leave Status unset.
