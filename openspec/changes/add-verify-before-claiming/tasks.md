## 1. Canonical skill

- [x] 1.1 Create `skills/verify-before-claiming/SKILL.md` with the 5 contracted frontmatter keys,
      `metadata.category: process`, and a description carrying pt-BR + English triggers plus four
      `Do NOT use for` boundaries
- [x] 1.2 Body: the claim definition (asserted **or acted on**), `## CRITICAL: Ground rules` in the
      numbered `**Bold lead** — explanation` shape used by `backlog/SKILL.md:36-51`
- [x] 1.3 Body: the research ladder (rungs 0-6), its stop condition, the never-skip-downward rule,
      the rung-4/5-depends-on-rung-2 rule, and offline degradation
- [x] 1.4 Body: the cost rule (when the ladder does **not** run) and the anti-theater clause
- [x] 1.5 Body: claim labelling (verified / inferred / unknown), the load-bearing threshold, and the
      in-code `UNVERIFIED:` comment rule
- [x] 1.6 Body: the not-found protocol and the ban on substituting a plausible answer
- [x] 1.7 Body: the knowledge-cutoff rule and the off-script guard, the latter linking to
      `execute-backlog` for deviation bookkeeping instead of restating it
- [x] 1.8 `references/research-ladder.md` — per-ecosystem lockfile and installed-source locations,
      probe recipes, version-pinned documentation URLs, offline degradation table
- [x] 1.9 `references/report-templates.md` — the three labels, the not-found report, the
      Doing/Not-doing/Assumptions block, the mid-flight scope-change report
- [x] 1.10 `references/failure-catalog.md` — anti-pattern table where every row names the defect that
      earned it, plus the add/remove rule
- [x] 1.11 Probe every command the skill prescribes on this machine and record the tool versions and
      the date in the skill body

## 2. Cross-links and canonical map

- [x] 2.1 `skills/documentation/SKILL.md` — shrink lines 34-36 to one line + link; add a `See also`
      bullet
- [x] 2.2 One-line link in `bug-hunter`, `api-resilience-testing`, `backlog`, `execute-backlog`,
      `assettoserver-csp-lua`, `assettoserver-plugin`, `helm-migration`, `openspec-drivezone`
- [x] 2.3 Bump `metadata.version` on every touched skill

## 3. Catalog composition

- [x] 3.1 `README.md` — new row in the Process & git table
- [x] 3.2 `generate.sh` `GROUP_DESC[workflow]` and `.claude-plugin/marketplace.json`
      `ai-skills-workflow` description name the new skill
- [x] 3.3 Run `./generate.sh` and commit the regenerated `claude/ codex/ cursor/ copilot/ plugins/`

## 4. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Every skill added or edited
     by this change gets checked against the skills-authoring spec. Keep the group number
     as the second-to-last group. -->

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [x] Q.2 All touched skill content in English (catalog locale)
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [x] Q.5 `python3 scripts/validate-skills.py` exits 0 (C1 reference paths, C2 cross-skill refs,
      C3 code blocks parse, C4 description vs body, C6 fence tags, C8 no meta sections)
- [x] Q.6 `python3 scripts/selftest-validate-skills.py` and `python3 scripts/scan-secrets.py` pass
- [x] Q.7 No `## How to Use` / `## Usage` / `## Prompt` / `## Trigger Test Cases` section anywhere in
      the new skill (check C8 would fail the build)

## 5. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [x] V.1 `openspec validate add-verify-before-claiming --strict` green
- [x] V.2 Catalog discovery intact: every skill directory carries a `SKILL.md` whose `name` matches
      it, at the expected count of 33, with no orphan or renamed leftovers
      (`bash scripts/validate-rite.sh` + the C7 orphan check inside `validate-skills.py`)
- [x] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive add-verify-before-claiming --yes` after all groups above are `[x]`
      — per this repo's established sequence this happens in a follow-up PR after the
      implementation PR merges (precedent: PR #61 shipped the active change, PR #62 archived it)
