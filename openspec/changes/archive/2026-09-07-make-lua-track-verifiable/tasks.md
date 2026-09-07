## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at. Read at `28d0c80` on 2026-09-07:
      `skills/bug-hunter/references/track-fivem-lua.md` (the three probed claims and the paragraph
      that prescribes the by-hand witness), `skills/bug-hunter/references/track-python-pytest.md`
      (the shape a track with a method looks like), `skills/bug-hunter/SKILL.md` (the version block
      that already carves out the Lua track), `openspec/specs/skills-catalog/spec.md` (the
      requirement this change modifies, five scenarios, carried whole into the delta),
      `scripts/validate-rite.sh` and `scripts/validate-skill-version.py` (the header shape a script
      in this repository owes) and `scripts/validate-agents.py` (how a missing dependency is reported
      as a skip and not a pass).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded.
      `luarocks --version` -> `3.13.0`, `lua -v` -> `Lua 5.5.0`, `busted --version` -> `2.3.0`.
      `luarocks install lua-quickcheck --check-lua-versions` ->
      `lua-quickcheck supports only Lua 5.1 and Lua 5.2 but not Lua 5.5.`;
      `luarocks search mutmut`, `... mutation-testing`, `... luamutant` each -> a header and an empty
      result set. The example itself was run before being published: a five-case `busted` spec over a
      pure clamp module -> `5 successes / 0 failures / 0 errors`, and with the clamp's own constant
      moved from 100 to 101 -> the case that asserts the value at the maximum turned red with
      `Expected objects to be equal. Passed in: (number) 101 Expected: (number) 100`. `busted` is not
      on `PATH` after `--local` (`command not found: busted`) until `eval "$(luarocks path --bin)"`.
- [x] E.3 Anything that could NOT be probed is written down as an open question — never stated as
      fact, never filled with a plausible substitute. One: whether a `lua-quickcheck` built for Lua
      5.4 would work against CfxLua is still unknown, because no 5.4 rock exists to install. That
      was already recorded when the track was written and does not change here; the script this
      change adds is what would surface the day a 5.4 rock appears.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed: the `.NET` track could carry the
      same treatment the day a runtime is available to probe it — it is not, and inventing the
      equivalent script blind is the defect this whole line of work exists against.

## 2. The example

- [x] 2.1 The track carries a pure Lua module with one limit and the `busted` spec that proves that
      limit on each side and at the value
- [x] 2.2 The example is the only copy: the script reads it out of the track

## 3. The probe

- [x] 3.1 `scripts/probe-lua-track.sh` extracts the blocks from the track, runs them, and requires green
- [x] 3.2 It moves the limit constant by one and requires the suite to go red — an example that
      catches nothing demonstrates nothing
- [x] 3.3 It re-runs the three ecosystem claims and fails naming whichever stopped holding
- [x] 3.4 A missing `luarocks` is reported as a skip with a non-success exit, never as a pass
- [x] 3.5 The header declares what the script does not cover, including why it is not in CI
- [x] 3.6 `bug-hunter` version bumped and the probe recorded in its version block; `./generate.sh` run

## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact is a script and its entry point is running it. `bash scripts/probe-lua-track.sh`
      -> `env luarocks 3.13.0  Lua 5.5.0`, `OK claim 1 holds: lua-quickcheck still supports only Lua
      5.1 and 5.2`, `OK claim 2 holds for 'mutmut': no result` (and for the other two rocks),
      `extract 10 lines of module, 13 lines of spec`,
      `OK the published example runs green: 5 successes / 0 failures / 0 errors`,
      `OK the example witnesses the moved limit: 4 successes / 1 failure`,
      `lua-track probe OK — every claim the track publishes still holds.`, exit `0`.
- [x] S.2 Case matrix measured, as counts. Paths that had to succeed and did, **1/1** (exit `0` on
      the published track). Paths that had to fail and did, **2/2**: with the two cases at the value
      deleted from the track's spec, `FAIL the example did NOT witness the moved limit — MAX 100 ->
      101 left the suite green`, exit `1`; with the fenced blocks renamed,
      `ERROR could not extract clamp.lua from the track`, exit `1`. Path that had to report a skip and
      did, **1/1**: run with `luarocks` off `PATH` ->
      `SKIP luarocks is not installed — this is a SKIPPED probe, not a pass.`, exit `2`. Ecosystem
      claims re-established, **4/4** (one version check, three rock searches).
- [x] S.3 Two, both in the script and both caught by running it rather than by reading it.
      (1) The first version did not parse at all — `unexpected EOF while looking for matching`
      backtick — because an error message inside double quotes contained a fenced-block marker, which
      bash read as command substitution. (2) The witness line printed an empty count, because busted
      says `1 failure` in the singular and the pattern asked for `failures`; the moved-limit check was
      passing while reporting nothing, which is the shape of a check that looks like it works. Both
      fixed and re-run. Nothing else behaved unexpectedly.

## 5. Quality Gates (MANDATORY)

- [x] Q.1 `python3 scripts/validate-skills.py` -> `skills checked: 38   findings: 0`;
      `validate-skill-version.py` -> `1 skill(s) changed`, `bug-hunter` 2.6.0 -> 2.7.0
- [x] Q.2 Track, version block and script are English; the identifier gate over the staged diff ->
      `findings: 0`
- [x] Q.3 No `description` and no trigger surface is touched
- [x] Q.4 No doctrine restated: the witness rule stays in the track's own section and the
      read-survivors-by-class rule is applied, not copied
- [x] Q.5 The two Lua blocks use English identifiers only — `clamp`, `value`, `MIN`, `MAX`

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate make-lua-track-verifiable --strict` ->
      `Change 'make-lua-track-verifiable' is valid`; `bash scripts/validate-rite.sh` -> `rite gate OK`
- [x] V.2 `npx -y skills add . --list` -> 44 skills, the 38 under `skills/` plus the 6 under
      `.claude/skills/`; nothing added, removed or renamed
- [x] V.3 Composition unchanged; the README paragraph on the gates names no script list, so it
      stays accurate
- [x] V.4 `openspec archive make-lua-track-verifiable --yes` — run after PR #240 merged (`7eca86e`),
      under issue #244. Output: `Applying changes to openspec/specs/skills-catalog/spec.md: ~ 1
      modified`, `Totals: + 0, ~ 1, - 0, → 0`, archived as `2026-09-07-make-lua-track-verifiable`.
      Measured either side: `skills-catalog` stays at **39 requirements** with every title identical,
      and goes from **185 to 188 scenarios** — *A declared absence carries its re-measurement*,
      *A published method is executable from the text* and *A check that cannot run says so*. No
      existing scenario lost, checked by set difference in both directions.
