## Context

This repository's gates are layered and each is honest about its own limits. What they are not is
complete: every one of them is scoped to a subtree or a file class, and the two defects that
prompted this change both lived in the gap between them.

## Goals / Non-Goals

**Goals:**

- Make both defect classes fail the build instead of relying on a reader noticing a diff.
- Keep the gate cheap enough that it never becomes the reason a green build is doubted.
- State the blind spots inside the checks, so a passing run is not read as coverage it does not have.

**Non-Goals:**

- Cataloguing every artifact class that could theoretically be committed. H1 covers exactly the
  bytecode rules `.gitignore` names, because that is what actually leaked.
- Purging the `.pyc` blob already published in `2.6.0`. Settled previously: rewriting a public branch
  costs every consumer a re-clone to remove one inert artifact.

## Decisions

**A gate, not a generator.** The recorded follow-up asked whether the skill count should be
*generated* into `README.md` rather than written by hand. Rejected: templating a hand-edited Markdown
document adds a build step to the one file every reader opens first, and it would make the README a
generated artifact that `git diff` can no longer be reasoned about directly. A check that fails the
build on drift gets the same guarantee and leaves the document plain.

**`git ls-files`, not a filesystem walk.** H1 must fire on a file forced in with `git add -f` and
must **not** fire on an ignored `__pycache__` sitting in a developer's working directory. Only the
index distinguishes those two, and confusing them would make the gate noisy enough to be disabled.

**H2's pattern is narrow, and its blind spot is written into the check.** It matches the literal
shape `all N` in two named files. A count phrased another way escapes it. That limit is not
hypothetical — it is the exact failure that already happened here: the first sweep hunting these
counts used a pattern requiring the word "skills" after the number and missed `all 30.` in
`README.md`, which has no noun after it. Declaring the blind spot is required by
`openspec/specs/skills-authoring` → *Authoring rules are machine-enforced* ("A check that covers only
**part** of its rule SHALL state the uncovered part in the check itself").

**The gate is itself gated.** `--selftest` injects one defect per check into a throwaway copy and
asserts detection, because a catalog with zero findings and a check that cannot fire are otherwise
indistinguishable. Both the gate and its self-test run in CI, matching the existing pair.

**Standard library only.** The CI job installs `pyyaml` for `validate-skills.py` and nothing else.
A hygiene gate that adds a dependency costs more than the defects it prevents.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| "Never hand-copy what a tool generates; link or generate it" | `documentation` | already canonical — H2 is that rule enforced mechanically on this repo's own docs; nothing is restated |
| Hand-copied facts that drift; re-derive rather than recall | `verify-before-claiming` | already canonical — H2 automates the derivation its *Hand-copied fact that drifted* row describes; the doctrine is not duplicated |
| Adversarial validation: prove a checker fires before trusting it | `bug-hunter` | already canonical — `--selftest` applies it; no methodology is reproduced |
| "A check that covers only part of its rule states the uncovered part" | `openspec/specs/skills-authoring` (spec, not skill) | already canonical — applied by the `KNOWN LIMIT` paragraph in each check's docstring |

No skill file is modified by this change, so no cross-cutting rule moves home.

## Risks / Trade-offs

- **H2 false-positives on an unrelated `all N` phrase** in the two files → the pattern is narrow and
  the file list is two entries; a false positive fails loudly and is fixed in a line, which is
  strictly better than the silent staleness it replaces.
- **H1 gives a false sense of completeness** — a tracked `.so`, `.class` or minified bundle passes →
  stated in the check's `KNOWN LIMIT` rather than implied away.
- **One more gate to keep green** → it costs nothing on a clean tree and fires only on the two
  defects that already occurred here.

## Migration Plan

Additive. The current tree passes both checks, so the gate is green from its first run. Rollback is
deleting the script and its two CI steps; nothing depends on it.

## Open Questions

None. The one question this change inherited — generate the counts or gate them — is answered under
*Decisions* rather than deferred again.
