## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at. Read at `501b3cf` on 2026-09-07:
      `skills/bug-hunter/SKILL.md` (2.5.0, the enumerate/generate/score section and its `lean:`
      ceilings), `skills/bug-hunter/references/track-python-pytest.md` (the shape the other two
      tracks are measured against), `skills/bug-hunter/references/track-fivem-lua.md`,
      `skills/bug-hunter/references/track-dotnet-plugin.md`,
      `openspec/specs/skills-catalog/spec.md` (the requirement this change modifies, published by
      the archived change `2026-09-07-update-bug-hunter-generation-and-scoring`) and
      `openspec/specs/skills-authoring/spec.md` (the rule that a prescribed step carries its command).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded.
      `command -v lua luarocks busted dotnet mono` -> `lua` and, after `brew install luarocks`,
      `luarocks 3.13.0`; `busted`, `dotnet` and `mono` absent before the install, `dotnet` and `mono`
      absent after. `lua -v` -> `Lua 5.5.0`. `luarocks --local install busted` ->
      `busted 2.3.0-1 is now installed`. `luarocks --local install lua-quickcheck` ->
      `Error: No results matching query were found for Lua 5.5.`;
      `luarocks install lua-quickcheck --check-lua-versions` ->
      `lua-quickcheck supports only Lua 5.1 and Lua 5.2 but not Lua 5.5.` For the scoring layer,
      `luarocks search mutmut`, `luarocks search mutation-testing` and `luarocks search luamutant`
      each returned a header and an empty result set. Re-verified after the fact, on the maintainer's
      request that the install be proved usable and not merely present: `busted --version` -> `2.3.0`,
      and a five-case spec over a pure clamp module -> `5 successes / 0 failures / 0 errors`. The
      install alone is NOT enough — `--local` puts the binary in `~/.luarocks/bin`, off `PATH`, and a
      shell without `eval "$(luarocks path --bin)"` answers `command not found: busted`. That second
      step was missing from the track as first written and is now in it.
- [x] E.3 Anything that could NOT be probed is written down as an open question — never stated as
      fact, never filled with a plausible substitute. Two. **Stryker.NET was not run**: no .NET SDK
      is present (`command -v dotnet` -> absent), so the .NET track names it only as the tool a
      reader will reach for, marked unprobed, and prescribes nothing about it. **Whether
      `lua-quickcheck` would work against CfxLua if built for 5.4 is unknown**: no 5.4 rock exists to
      install and building one is outside this change. Both are recorded in `design.md` under
      *Open questions*.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed: (a) `busted 2.3.0-1` installs
      cleanly on Lua 5.5 and the Lua track could grow a runnable example suite rather than only
      naming the runner — separate item, since it is about the enumeration layer this change does not
      touch; (b) whether the catalog should carry a probe script that re-runs these ecosystem checks
      on a schedule, so a track's declaration ages visibly instead of silently.

## 2. The two tracks

- [x] 2.1 `references/track-fivem-lua.md`: both layers answered, each statement carrying the command
      that produced it, and what the rite does where the ecosystem offers nothing
- [x] 2.2 `references/track-dotnet-plugin.md`: the scoring question answered by what the track
      already prescribes for its failure class, and Stryker.NET named as unprobed
- [x] 2.3 `skills/bug-hunter/SKILL.md`: version 2.5.0 -> 2.6.0 and the version block records this
      probe; `./generate.sh` run

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point. The two tracks were staged into
      the live plugin cache and read by a fresh process; the cache was restored afterwards.
      `claude -p` loading `Skill(ai-skills-testing:bug-hunter)` and asked what the Lua track
      prescribes -> `No. lua-quickcheck only supports Lua 5.1/5.2, CfxLua is 5.4-based, so library
      not reach runtime (probed luarocks 3.13.0, 2026-09-07)`; the same session asked about the .NET
      track -> `Not prescribed. Track calls it a pointer, not a prescription — catalog never ran it
      (no .NET SDK present, command -v dotnet absent, 2026-09-07), no command given`.
- [x] S.2 Case matrix measured, as counts: questions the loaded skill had to answer from the track
      and answered correctly, **4/4** — the generation refusal with its reason, the scoring absence
      with the three searches, what the rite does instead, and the unprobed status of Stryker.NET.
      Ecosystem probes run: **5/5** answered (`lua -v`, `luarocks --version`, the `busted` install,
      the `lua-quickcheck` version check, the three empty mutation searches). Tools this change
      prescribes without having run them: **0/0**.
- [x] S.3 One expectation of mine was wrong and is recorded because it changed the change: I expected
      `lua-quickcheck` to be installable and the Lua track to end up with a prescribed generator.
      LuaRocks refused it for the installed Lua and named the supported versions, which is what turned
      the section from a prescription into a probed declaration — the better outcome, and one I would
      have guessed wrong. **And one escape, in this change's own text**: the track first said the
      runner "installs cleanly" and stopped there. It does install; it does not RUN, because
      `~/.luarocks/bin` is not on `PATH`. Caught only when the install was exercised end to end
      afterwards — `command not found: busted` — which is the same lesson as issue #95: present is not
      the same as working. The `PATH` step and a proved five-case run are now in the track, and moving
      the clamp constant from 100 to 101 was verified to turn the value witness red while `>` widened
      to `>=` survived as a genuinely equivalent mutant.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 `python3 scripts/validate-skills.py` -> `skills checked: 38   findings: 0`, which owns
      every field in this box, and `validate-skill-version.py` -> `1 skill(s) changed` with
      `bug-hunter` 2.5.0 -> 2.6.0
- [x] Q.2 Both tracks and the version block are English; the commit body is Portuguese, which is
      the repository's prose language (`code-locale`)
- [x] Q.3 The `description` frontmatter is untouched, so the routing surface and the existing
      boundaries against `api-resilience-testing` and `tdd` are unchanged
- [x] Q.4 No doctrine restated: the criteria and the `lean:` ceilings stay in the stack-agnostic
      SKILL.md and the tracks point at them; `fivem-lua` and `assettoserver-plugin` keep their rules
- [x] Q.5 The new blocks are shell commands with English flags and rock names only

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate extend-bug-hunter-tracks-to-lua-and-dotnet --strict` ->
      `Change 'extend-bug-hunter-tracks-to-lua-and-dotnet' is valid`; `bash scripts/validate-rite.sh`
      -> `rite gate OK`
- [x] V.2 `npx -y skills add . --list` -> 44 skills, the 38 under `skills/` plus the 6 under
      `.claude/skills/`; nothing added, removed or renamed
- [x] V.3 Composition unchanged. `README.md:670` already reads `enumerate / generate / score` for
      this skill and names the three tracks, which stays accurate now that all three answer both
      layers
- [ ] V.4 `openspec archive extend-bug-hunter-tracks-to-lua-and-dotnet --yes` — left for after the
      merge, as in #224, #208 and #195; the pull request reports the change as active and names this
      as what closes it
