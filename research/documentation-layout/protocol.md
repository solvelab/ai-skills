# Protocol

What was decided **before** any number existed, so a reader can tell a measurement from a
rationalisation. Everything here was fixed in the change's `design.md`, committed at `59dc13c`,
before the detector existed and before any repository was scanned.

## The question

The `documentation` skill is being changed from a set of conditions ("a project earns a setup guide
when setup takes more than five commands") to a closed map ("the tutorial slot is called
`docs/en/SETUP.md`"), plus an ownership rule, plus a two-language pair, plus a detector that audits
the layout of a repository.

Three things have to be measured, not asserted:

1. **Is the problem real, and how large?** How many names does the fleet use for one concept, and
   how many repositories carry more than one of them at once.
2. **Does each detector rule find real defects, or does it reprove correct documents?** Findings per
   rule, confirmed one by one by hand.
3. **Does the changed skill actually produce the map when a real session runs it?** Not "does the
   text say so" — does a session, through the install path a user takes, leave that layout behind.

## The thresholds, fixed in advance

- **A rule ships as a gate only if its measured noise is below the level this catalog has already
  rejected.** That level is R6's: 7 wrong findings in 10, which is why R6 ships review-only
  (`skills/documentation/references/information-architecture.md`). A layout rule at or above that
  ratio ships review-only with its count, never as a gate.
- **No allowlist before the measurement.** A rule is measured first, and only then may it grow an
  exclusion. An allowlist written before the run is a way of not measuring.
- **A rule with zero findings on the fleet is proved by its injected defect, or it is not proved.**
  Zero findings is not evidence of correctness; R4 and R7 carry that same caveat.
- **The simulation is the gate a green self-test cannot replace.** A rule that passes its own
  self-test and a checker that runs clean still say nothing about what a session does with the
  skill. The artifact is exercised through a real install path, on a real repository, and what is
  recorded is what was observed.
- **Spend ceiling for the simulation: US$ 5, in one pass.** Declared before the first cell ran. If
  the two runs exceed it, the run stops and the result is reported as partial — the ceiling is not
  raised mid-measurement.

## The verdict, written before the numbers

| Outcome | What it means | What happens |
|---|---|---|
| **SHIP** | every rule under R6's noise level, and the simulation produces a layout inside the map | the change publishes as written |
| **TRIM** | one or more rules above that level | those rules ship review-only, with their count, and the rest publish |
| **REWRITE** | a run produces a layout the map does not describe, or the pair costs more than the ceiling allows | the affected part is redesigned first; no partial claim is made |

## Pass 1 — inventory

```bash
python3 research/documentation-layout/survey.py --root <workspace> --inventory --markdown
```

Every git repository at depth ≤ 3 under the workspace. Counts `.md` at depth ≤ 2 inside each one —
the root and one level below it, which is where every tier document of the map lives. Reports the
spellings found per concept, the repositories carrying two names for the explanation slot, and the
transient records outside `docs/reports/`.

## Pass 2 — detector

```bash
python3 research/documentation-layout/survey.py --root <workspace>
```

Runs `skills/documentation/references/check-doc-layout.py` over each repository and aggregates
findings per rule. **The false-positive column is not computed by the script.** Confirming a finding
means opening the repository and reading it, one finding at a time; `results.md` records who did that
and on which date, and every unconfirmed finding is reported as a false positive rather than
quietly dropped.

## Pass 3 — simulation

Two repositories, copied to a throwaway directory and stripped of their git history:

- one that runs a spec-driven workflow, to exercise the rule that `REQUIREMENTS.md` indexes the
  capabilities instead of copying them;
- one that does not, to exercise the same slot with no workflow to point at.

The changed skill is installed the way the catalog publishes it into a project
(`.claude/skills/documentation/`, the layout `generate.sh` writes), a git repository is initialized
so the session resolves project skills, and the session is asked to document the repository in the
words a user would use. What is recorded is the command, a fragment of the observed output, the
files that appeared, and the detector's verdict on the result.

The measurement is the layout, not the prose: the map is a claim about which files exist and what is
inside them, and that is what is checked.
