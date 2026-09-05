# CI step — the identifier-locale gate on every pull request

One job, copy-paste. It downloads the detector the `code-locale` skill ships at a **tagged release**
of `solvelab/ai-skills`, verifies its digest, and measures only the lines the pull request adds.
No clone of the catalog, no assistant, no Python package: `python3` 3.9+ and `curl` are already on
`ubuntu-latest`.

```yaml
name: identifier-locale

on:
  pull_request:

permissions:
  contents: read

jobs:
  identifier-locale:
    name: Identifier locale (added lines are English)
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Fetch the detector, pinned
        env:
          AI_SKILLS_TAG: v2.21.0
          CHECK_SHA256: 4e72af47225d6259f6b69db638af6db6c586c7ee6800e401941e08c223413ff2
        run: |
          curl -fsSL -o check-identifier-locale.py \
            "https://raw.githubusercontent.com/solvelab/ai-skills/${AI_SKILLS_TAG}/skills/code-locale/references/check-identifier-locale.py"
          echo "${CHECK_SHA256}  check-identifier-locale.py" | sha256sum -c -

      - name: Identifier locale on the lines this pull request adds
        run: |
          git diff origin/${{ github.base_ref }}...HEAD | python3 check-identifier-locale.py --diff - --no-english
```

## Why each line is there

- **`on: pull_request` only.** The command diffs the branch against its base, and `github.base_ref`
  exists only on `pull_request` events — on `push` it is empty and `git diff origin/...HEAD` has
  nothing to measure. A gate that cannot measure must not approve, so it is not wired where it
  cannot run.
- **`fetch-depth: 0`.** `git diff A...HEAD` measures from the merge base. The default depth of 1
  leaves no base revision in the clone and the diff fails or measures the wrong thing; the
  catalog's own `ci.yml` carries the same setting for the same reason.
- **`persist-credentials: false`.** Nothing after the checkout needs the token; the default leaves
  it in `.git/config` for every later step.
- **`permissions: contents: read`.** The job reads the repository and nothing else.
- **The pin.** `AI_SKILLS_TAG` is a release tag of `solvelab/ai-skills`, never `master`: a gate on
  a moving branch fails your pull requests on someone else's release schedule. `CHECK_SHA256` is the
  digest of the detector **at that tag** — `sha256sum -c` fails the step on any other content, so
  the tag cannot drift under you and a compromised or mistyped URL cannot run. Bump the two
  together:

  ```bash
  TAG=v2.22.0
  curl -fsSL "https://raw.githubusercontent.com/solvelab/ai-skills/${TAG}/skills/code-locale/references/check-identifier-locale.py" | sha256sum
  ```

  The value shipped above (`4e72af47…3ff2`) is the detector at `v2.21.0`, measured on 2026-09-05.
- **`--diff -`.** Added lines only. Whole-tree enforcement turns a legacy repository red on day one
  and a gate that blocks every pipeline is switched off within a week — the detector's docstring
  records this as the reason `--diff` exists. Existing names migrate by the skill's tiers
  (`references/migration.md`), not by this step.
- **`--no-english`.** The advisory "is this word English?" tier needs the three word-list files
  that sit beside the detector in the catalog (`english-words.txt.gz`, `programming-words.txt`,
  `not-english.txt`). Without them every segment would be reported as unknown — measured, not
  assumed. The gating tiers (`pt-verb`, `pt-noun`, `pt-morphology`, path) do not depend on those
  lists, so the exit code is identical with or without this flag. Want the advisory tier in CI?
  Download the three files beside the detector (same URL shape, same tag) and drop the flag.
- **The pipe's exit code.** A `run:` block on Linux runs `bash -e {0}` **without** `pipefail`, so
  the step's status is `python3`'s — exactly what is wanted: exit 1 on a gating finding, 0
  otherwise. A `git diff` failure (no base revision) prints its error and the detector, reading an
  empty diff, reports `findings: 0`; that is why `fetch-depth: 0` is not optional here.

## Reading a failure

The detector prints `path:line:token [tier]` and the exact waiver line to add. The exits are the
skill's, not this step's: `# locale-ok: <reason>` on the offending line or the one above it; the
`.identifier-locale-allow` file for a file or directory name; and, for a term with no faithful
English name, the change's glossary (`references/glossary-protocol.md`). Doctrine and the reading
guide: the skill's *Reviewing a diff* section.

## What this step does not cover

- **Pushes to the default branch.** It runs on pull requests only. A repository that accepts direct
  pushes has no gate on them here; branch protection is what closes that.
- **Content outside the detector's `EXT_LANG`** (`.py .lua .js .jsx .mjs .cjs .ts .tsx .cs .sql .yml
  .yaml .json .sh .bash`): the path of an added file is still measured; its content is reported as
  skipped, never as passing.
- **Existing content.** Only added lines. A pull request that moves a legacy Portuguese name from
  one file to another adds it, and is reported — that is the migration policy meeting the gate, and
  the waiver line is the answer when the move is deliberate.
- **The advisory tier**, unless you ship the word lists and drop `--no-english`.
- **Everything the detector's own `KNOWN LIMIT` list names** — words that are both English and
  Portuguese, abbreviations under the minimum segment length, identifiers built at runtime, Spanish
  and Italian. A green step is a measurement of what the tiers reach, not proof of compliance.
- **Other CI systems.** The one-line command is the whole contract; the YAML around it is GitHub
  Actions. On GitLab CI the base is `$CI_MERGE_REQUEST_TARGET_BRANCH_NAME` with `GIT_DEPTH: 0`; the
  pin and the digest check are the same.

For the layer that catches the name **before** it reaches a pull request — the human's own
`git commit` — see `references/pre-commit-locale.sh`.
