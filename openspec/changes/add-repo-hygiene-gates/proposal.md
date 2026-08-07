## Why

Two defects of the same class landed in this repository within one day, and neither was caught by a
gate — both were found by a human reading a diff. A `.pyc` was tracked and shipped in release
`2.6.0`, and three published skill counts had drifted to 27 and 30 against a tree of 32.

Both were fixed and both were recorded as follow-ups rather than gated, which left the repository in
the state its own doctrine warns about: the truth was restored by hand and is now defended by a note
asking a human to remember.

The reason nothing caught either is structural. Every existing gate looks at one slice —
`scripts/validate-skills.py` walks `skills/`, `scripts/scan-secrets.py` hunts credentials,
`scripts/validate-rite.sh` reads OpenSpec changes, and CI's wrapper-sync step diffs generated trees.
Nothing looks at the repository as a whole.

## What Changes

- Add `scripts/validate-repo-hygiene.py`, a whole-repository gate with two checks:
  - **H1** no compiled Python artifact is tracked;
  - **H2** every `all N` skill count in `README.md` and `.claude-plugin/marketplace.json` equals the
    number of directories under `skills/`.
- Add a `--selftest` mode that injects one known defect per check into a throwaway clone and asserts
  detection, on the same principle as `scripts/selftest-validate-skills.py`.
- Each check declares in its own docstring what it does **not** cover.
- Wire both the gate and its self-test into `.github/workflows/ci.yml`, and document them in the
  README's enforcement section.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skills-catalog`: the catalog gains a gate whose subject is the repository itself rather than the
  skills in it, closing the slice every existing gate leaves uncovered.

## Impact

- `scripts/validate-repo-hygiene.py` — new; standard library only, reads the tree via `git ls-files`,
  writes nothing outside a temporary directory during `--selftest`.
- `.github/workflows/ci.yml` — two new gating steps.
- `README.md` — enforcement section describes the gate and its blind spots.
- No skill, no generated tree and no OpenSpec spec content changes, so nothing regenerates and no
  consumer behaviour changes.
- **A stale published count now fails the build.** Any future change that adds or removes a skill
  must update the counts in the same commit, which is the point.
