# Change: Make the authoring requirements executable, and fix what they catch

## Why

Three audits added four requirements to `skills-authoring` — Simulated failure behaviour, Description
agrees with body, Code blocks compile or are marked, Versioned external APIs are pinned. All four were
convention only. Nothing in CI could tell whether a skill obeyed them, which is exactly the failure
mode `skills-authoring` already names: *"Advisory mechanisms are not sold as hard gates."*

A validator was written for the mechanically checkable half and run over all 30 skills. First pass:
**31 findings**. Triaging them honestly, **22 were the validator's own bugs**, not the catalog's:

| validator defect | effect |
|---|---|
| scanned paths inside fenced blocks | template content counted as broken links |
| scanned links inside inline-code spans | a rule *showing* link syntax counted as a broken link |
| resolved `references/x.md` from the file's own directory | reference-to-reference citations counted as missing |
| did not dedent fences nested in list items | correct Python read as `IndentationError` |
| "looks like CSS" heuristic matched `import {` | a valid multi-line import counted as mistagged |
| absolute-promise heuristic matched prohibitions | "never leaks a token" counted as a scope contradiction |
| version-pin regex missed stated stacks | "pydantic v2 / SQLAlchemy 2" counted as unpinned |

After fixing the instrument: **9 real findings**, all now fixed. The remaining zero is verified by an
adversarial self-test that injects one known defect per check and asserts the validator fires —
**10/10 detected**. A checker that never fails is not a checker.

## What Changes

- New `scripts/validate-skills.py` — six checks over every `skills/*/SKILL.md` and its references:
  C1 referenced repo paths exist · C2 cross-skill references name a real skill · C3 code blocks parse
  (bash/yaml/json/lua/python) · C4 description agrees with body · C5 versioned APIs are pinned ·
  C6 fence tags match content. Reports which checks were skipped for want of a tool.
- New `scripts/selftest-validate-skills.py` — mutates a throwaway copy of the catalog once per check
  and asserts detection. The gate is itself gated.
- Both wired into the CI `validate` job.
- Real defects fixed:
  - **7 cross-skill reference paths** cited as if local — `references/track-python-pytest.md` from
    `python-rest-api`, and the same for `assettoserver-csp-lua`, `assettoserver-plugin`, `fivem-lua`,
    `openspec-drivezone`, `execute-backlog` — now name the owning skill
    (`bug-hunter/references/…`, `backlog/references/…`).
  - **helm-migration**: the description promised "Always generates both files when applicable" while
    the body says *"If the source YAML has no secrets, configmaps or PVCs, do not generate env.yaml."*
    The description now names the condition. Also states that the local chart template is the source
    of truth, not the skill, so a field list that drifts is caught by reading the template first.
  - **5 blocks** in `negative-test-catalog.md` tagged `json` while containing several
    comment-annotated payload variants — retagged `jsonc`.
  - **2 fragments** tagged `lua` and `python` marked as excerpts, matching the r3f convention.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — the mechanically checkable authoring rules SHALL be enforced
  by a script wired into CI, and that script SHALL carry a self-test proving each check fires.

## Impact

- `scripts/validate-skills.py`, `scripts/selftest-validate-skills.py`, `.github/workflows/ci.yml`.
- Skills corrected: `python-rest-api`, `fivem-lua` (+ reference), `assettoserver-csp-lua`,
  `assettoserver-plugin`, `openspec-drivezone`, `execute-backlog` (reference), `helm-migration`,
  `api-resilience-testing` (reference), `log-event-collector`.
- Every future skill change is now checked for the same six defect classes on every PR.
