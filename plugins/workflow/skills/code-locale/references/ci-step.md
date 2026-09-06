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
        env:
          PYTHONIOENCODING: utf-8:surrogateescape
        run: |
          set -o pipefail
          git diff --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ origin/${{ github.base_ref }}...HEAD \
            | python3 check-identifier-locale.py --diff - --no-english
```

## Why each line is there

- **`on: pull_request` only.** The command diffs the branch against its base, and `github.base_ref`
  exists only on `pull_request` events — on `push` it is empty and `git diff origin/...HEAD` has
  nothing to measure. A gate that cannot measure must not approve, so it is not wired where it
  cannot run.
- **`fetch-depth: 0`.** `git diff A...HEAD` measures from the merge base. The default depth of 1
  leaves no base revision in the clone and `git diff` fails — which, with `pipefail` below, fails the
  step instead of approving an empty diff; the catalog's own `ci.yml` carries the same setting for
  the same reason.
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
- **`set -o pipefail`.** The default shell of a `run:` block on Linux is `bash -e {0}` (GitHub's
  workflow-syntax page; not probed on a runner here), and `-e` alone takes the pipe's status from its
  **last** command. Without `pipefail` a failed `git diff` — a base ref that was not fetched, an empty
  `github.base_ref`, a `fetch-depth` left at 1 — prints its error, the detector reads an empty
  stream, prints `findings: 0`, and the step is green: measured on 2026-09-05 with the block verbatim
  (`fatal: ambiguous argument 'origin/release/9...HEAD'` then `findings: 0`, exit 0). With `pipefail`
  the same case exits 128. A gate that cannot measure must not approve, and this is the line that
  makes the step obey its own rule. The same effect comes from declaring `shell: bash`, which the same
  page documents as `bash --noprofile --norc -eo pipefail {0}`; the explicit line travels to other CI
  systems unchanged.
- **The four `git diff` flags.** They pin the diff's *shape*, so a runner's or a repository's git
  config cannot change what the detector reads — the pre-commit hook passes the same four, for the
  same measured reasons (its header, *WHAT IT DOES*): `--no-ext-diff` (a `diff.external` driver
  replaces the unified diff with its own output — an empty stream and `findings: 0`), `--no-renames`
  (with rename detection, git's default, `git mv orders.py relatorio.py` is a `rename to` header with
  no `--- /dev/null`, and the detector never measures the new name; without it a rename is a delete
  plus an add and the new path is measured), `--src-prefix=a/ --dst-prefix=b/` (`diff.mnemonicPrefix`
  writes `+++ i/…`, and a path grandfathered in `.identifier-locale-allow` stops matching). A fresh
  `ubuntu-latest` runner carries none of these settings; a self-hosted runner may.
- **`PYTHONIOENCODING: utf-8:surrogateescape`.** A hunk carrying non-UTF-8 bytes — a latin-1 legacy
  file, common in the codebases this skill targets — otherwise aborts the detector with
  `UnicodeDecodeError` before any name is judged, and the step fails for the wrong reason. With the
  handler the undecodable bytes pass through and only the names are measured.

## Reading a failure

The detector prints `path:line:token [tier]` and the exact waiver line to add. The exits are the
skill's, not this step's: `# locale-ok: <reason>` on the offending line or the one above it; the
`.identifier-locale-allow` file for a file or directory name; and, for a term with no faithful
English name, the change's glossary (`references/glossary-protocol.md`). Doctrine and the reading
guide: the skill's *Reviewing a diff* section.

## The prose direction, where the repository declares it

The identifier gate above is the whole step for a repository that has not declared its prose
language. A repository that carries `.code-locale` at its root (`prose: pt-BR` or `prose: en`; the
format, what is measured and what escapes are in the skill's section *Prose follows the repository*)
adds the two steps below. The prose detector imports the identifier detector **by path**, so it must
be downloaded beside it, together with the two word lists it reads; each file is pinned to the same
tag and digest-checked like the first one.

```yaml
      - name: Fetch the prose detector and its word lists, pinned
        env:
          AI_SKILLS_TAG: v2.21.0
          # sha256 of each file AT THE TAG — compute with the loop under "The pin"; a placeholder
          # fails `sha256sum -c` loudly, which is the correct outcome for an unpinned gate.
          PROSE_SHA256: <sha256 of check-prose-locale.py at the tag>
          PT_WORDS_SHA256: <sha256 of prose-words-pt.txt at the tag>
          EN_WORDS_SHA256: <sha256 of prose-words-en.txt at the tag>
        run: |
          base="https://raw.githubusercontent.com/solvelab/ai-skills/${AI_SKILLS_TAG}/skills/code-locale/references"
          for f in check-prose-locale.py prose-words-pt.txt prose-words-en.txt; do
            curl -fsSL -o "$f" "${base}/${f}"
          done
          printf '%s  %s\n' "${PROSE_SHA256}" check-prose-locale.py "${PT_WORDS_SHA256}" prose-words-pt.txt \
            "${EN_WORDS_SHA256}" prose-words-en.txt | sha256sum -c -

      - name: Prose locale on the lines this pull request adds (only where .code-locale declares it)
        env:
          PYTHONIOENCODING: utf-8:surrogateescape
        run: |
          set -o pipefail
          if [ ! -f .code-locale ]; then
            echo "prose direction off: no .code-locale at the repository root"; exit 0
          fi
          git diff --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ origin/${{ github.base_ref }}...HEAD \
            | python3 check-prose-locale.py --diff -
```

- **Both files in the same directory.** `check-prose-locale.py` reads `COMMENT_SYNTAX`, the waiver
  regex and the allowlist from `check-identifier-locale.py` beside it — nothing is duplicated, so
  nothing can drift; the cost is that the download must fetch both. The word lists are the evidence
  the classifier counts and ship beside the detector for the same reason as the English list of the
  identifier tier: the same fragment produces the same verdict on a laptop, in CI and inside the
  write-time hook.
- **Digests for the new files.** The value shipped above for the identifier detector was measured
  at `v2.21.0`; the prose files land in the first tag published after this change, so their digests
  are not written here — compute them with the loop under *The pin*, at the tag you pin, and paste
  them in. Until then the step fails at `sha256sum -c`, which is the correct behaviour of a gate with
  an unknown pin.
- **`[ -f .code-locale ]` before the run.** The detector itself is silent without the declaration
  (it prints `findings: 0` and says the direction is off); the guard only saves the download and
  makes the reason visible in the log. A declaration the detector cannot read exits 2 and fails the
  step, naming the file and the accepted values — never an unmeasured pass.
- **Exit semantics.** 1 only on a gating finding (a comment or docstring with strong evidence of
  the wrong language); a Markdown paragraph, or weak evidence, prints as advisory and exits 0. The
  exits are the skill's: translate it, `locale-ok: <reason>` on the fragment's line or the line
  above, or the path in `.identifier-locale-allow`.

## What this step does not cover

- **Pushes to the default branch.** It runs on pull requests only. A repository that accepts direct
  pushes has no gate on them here; branch protection is what closes that.
- **Content outside the detector's `EXT_LANG`** (`.py .lua .js .jsx .mjs .cjs .ts .tsx .cs .sql .yml
  .yaml .json .sh .bash`): the path of an added file is still measured; its content is reported as
  skipped, never as passing.
- **Existing content.** Only added lines. A pull request that moves a legacy Portuguese name from
  one file to another adds it, and is reported — that is the migration policy meeting the gate, and
  the waiver line is the answer when the move is deliberate. With `--no-renames` a **renamed file** is
  the same case: every line of the moved file is read as added, so renaming a legacy file whose
  content still carries Portuguese names turns the pull request red at that moment (fix the names,
  waive them, or grandfather the path). A pure rename of an English-clean file is silent; a rename
  **to** a Portuguese name is reported on the path, which is why the flag is there.
- **The advisory tier**, unless you ship the word lists and drop `--no-english`.
- **Prose, unless `.code-locale` declares the language** — and, with it, everything the prose
  detector's own `KNOWN LIMIT` list names: string literals and log messages, languages other than
  Portuguese and English, function words rather than a dictionary, text inside code fences, a block
  opened on a line the diff did not add.
- **Everything the detector's own `KNOWN LIMIT` list names** — words that are both English and
  Portuguese, abbreviations under the minimum segment length, identifiers built at runtime, Spanish
  and Italian. A green step is a measurement of what the tiers reach, not proof of compliance.
- **Other CI systems.** The one-line command is the whole contract; the YAML around it is GitHub
  Actions. On GitLab CI the base is `$CI_MERGE_REQUEST_TARGET_BRANCH_NAME` with `GIT_DEPTH: 0`; the
  pin and the digest check are the same.

For the layer that catches the name **before** it reaches a pull request — the human's own
`git commit` — see `references/pre-commit-locale.sh`.
