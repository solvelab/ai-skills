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
      each returned a header and an empty result set.
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

- [ ] 2.1 `references/track-fivem-lua.md`: both layers answered, each statement carrying the command
      that produced it, and what the rite does where the ecosystem offers nothing
- [ ] 2.2 `references/track-dotnet-plugin.md`: the scoring question answered by what the track
      already prescribes for its failure class, and Stryker.NET named as unprobed
- [ ] 2.3 `skills/bug-hunter/SKILL.md`: version 2.5.0 -> 2.6.0 and the version block records this
      probe; `./generate.sh` run

## 3. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 4. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

## 5. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate <id> --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive <id> --yes` after all groups above are `[x]`
