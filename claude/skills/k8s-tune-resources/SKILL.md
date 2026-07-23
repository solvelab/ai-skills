---
name: k8s-tune-resources
description: Bulk-edit Kubernetes resources requests/limits across many Bitbucket repos discovered from pods running on nodes with a given label. For each pod, derives the repo name from the image (segment after the last `/`, before `:`), clones `git@bitbucket.org:<ORG>/<REPO>.git`, checks out a target branch (default `deploy`), patches `deploy/dev/values.yaml` and `deploy/hml/values.yaml` with a sed pair, then commits and pushes. Use when the user asks to "tune", "reduce", "scale down" or "ajustar resources" of pods on nodes selected by a label (e.g. `apps=galileos`) across multiple repos.
metadata:
  author: diegops
  version: 1.0.0
  category: devops
---

# k8s-tune-resources

Skill for repeating the cluster-wide resources tuning routine across different Kubernetes clusters and label selectors.

## Required inputs (ask the user if missing)

1. **Node label selector** — e.g. `apps=galileos`
2. **Image-name prefix filter(s)** — substrings to grep on image names to pick which repos to touch (e.g. `galileo`, `ga-`)
3. **Bitbucket workspace/org** — e.g. `unearsa`
4. **Target branch** — default `deploy`
5. **values.yaml relative paths** — default `deploy/dev/values.yaml` and `deploy/hml/values.yaml`
6. **Patches (sed pairs)** — default:
   - `memory: "128Mi"` → `memory: "64Mi"`
   - `cpu: "50m"` → `cpu: "25m"`
7. **Commit message** — default `chore: reduce resources requests to 64Mi/25m in dev and hml`
8. **kubeconfig context** — confirm `kubectl config current-context` matches the cluster the user wants

## Workflow

### Step 1 — Discover repos

```bash
kubectl get nodes -l <LABEL>
```

For each node, list pods + container images and filter by the prefix(es):

```bash
for NODE in <node1> <node2> ...; do
  kubectl get pods -A --field-selector spec.nodeName=$NODE \
    -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{" "}{.spec.containers[*].image}{"\n"}{end}' \
    | grep -E '<PREFIX_REGEX>'
done
```

Extract repo name from image: segment after the last `/`, before `:` (strip tag). Dedupe.
Save list to `/tmp/<scope>-repos.txt` (one repo per line).

Show the list to the user and confirm scope before proceeding.

### Step 2 — Mass clone / edit / commit / push

Use `/tmp/<scope>-work/` as workdir.

```bash
LIST=/tmp/<scope>-repos.txt
WORK=/tmp/<scope>-work
ORG=<bitbucket-org>
BRANCH=<branch>
COMMIT_MSG="<commit-message>"
mkdir -p "$WORK"
LOG=$WORK/run.log
: > "$LOG"

status() { printf '%-60s %s\n' "$1" "$2" | tee -a "$LOG"; }

while IFS= read -r repo; do
  [ -z "$repo" ] && continue
  cd "$WORK" || exit 1

  if [ ! -d "$repo" ]; then
    if ! git clone --quiet "git@bitbucket.org:${ORG}/${repo}.git" 2>>"$LOG"; then
      status "$repo" "CLONE_FAIL"; continue
    fi
  fi

  cd "$WORK/$repo" || { status "$repo" "CD_FAIL"; continue; }
  git fetch --quiet origin 2>>"$LOG"

  if ! git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
    status "$repo" "NO_${BRANCH}_BRANCH"; continue
  fi

  git checkout --quiet "$BRANCH" 2>>"$LOG" || git checkout --quiet -b "$BRANCH" "origin/$BRANCH" 2>>"$LOG"
  git reset --quiet --hard "origin/$BRANCH" 2>>"$LOG"

  changed=0
  for f in deploy/dev/values.yaml deploy/hml/values.yaml; do
    if [ ! -f "$f" ]; then
      status "$repo:$f" "NO_VALUES_YAML"; continue
    fi
    sed -i \
      -e 's/memory: "128Mi"/memory: "64Mi"/' \
      -e 's/cpu: "50m"/cpu: "25m"/' \
      "$f"
    if ! git diff --quiet -- "$f"; then
      changed=1
      git add "$f"
    fi
  done

  if [ "$changed" -eq 0 ]; then
    status "$repo" "NO_CHANGE"; continue
  fi

  if ! git commit --quiet -m "$COMMIT_MSG" 2>>"$LOG"; then
    status "$repo" "COMMIT_FAIL"; continue
  fi
  if git push --quiet origin "$BRANCH" 2>>"$LOG"; then
    status "$repo" "PUSHED"
  else
    status "$repo" "PUSH_FAIL"
  fi
done < "$LIST"
echo "---DONE---" | tee -a "$LOG"
```

### Step 3 — Report

Summarize per-repo status from the log: PUSHED / NO_CHANGE / CLONE_FAIL / NO_<BRANCH>_BRANCH / NO_VALUES_YAML / COMMIT_FAIL / PUSH_FAIL.

## Safety notes

- This pushes to many repos. Always confirm scope (cluster context, label, image filter, list of repos) **before** running Step 2.
- Per global rule (`~/.claude/CLAUDE.md`): commit messages must **not** include any `Co-Authored-By: Claude` line.
- The sed patterns only match the literal strings `memory: "128Mi"` and `cpu: "50m"`. If a repo already uses other values (e.g. `256Mi`), it falls through as `NO_CHANGE`. Limits (`512Mi`, `1`) are preserved because they don't collide.
- If `deploy/dev/values.yaml` or `deploy/hml/values.yaml` is missing, the script skips that file but still commits/pushes the env that did change.
- Some repos store values at the repo root (`dev/values.yaml`) instead of under `deploy/`. Verify path on a sample repo first; adapt the `for f in ...` list if needed.

## Memorized facts

- Bitbucket org used so far: `unearsa`
- Branch used so far: `deploy`
- Cluster discovered via label `apps=galileos` had 2 nodes (`10.160.0.164`, `10.160.0.176`) and 51 galileo-related repos (28 `galileo*` + 23 `ga-*`) already patched on 2026-05-18.
