## 1. Evidence & Sources (MANDATORY)

- [ ] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
- [ ] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
- [ ] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
- [ ] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

## 2. Probe and pin — game and server skills (AssettoServer clone, DriveZone image, public stubs)

- [ ] 2.1 `assettoserver-ops`: every `extra_cfg.yml` key and the density function it quotes resolve in
      `~/works/AssettoServer` at `v0.0.55-pre25`; the DriveZone image reports its version; block + bump
- [ ] 2.2 `assettoserver-plugin`: TFM and package versions at `v0.0.54` read from the clone; the
      `0.0.55+51d8d8a6e0` / `net9.0` contradiction disclosed in the block; block + bump
- [ ] 2.3 `assettoserver-csp-lua`: the 15 `ac.*`/`ui.*` names resolve in `acc-lua-sdk` at a recorded
      commit; `snippets.lua` parses on Lua 5.4.8; in-game behaviour named as not probed; block + bump
- [ ] 2.4 `fivem-lua` and `fivem-fallback`: every fenced Lua block parses on Lua 5.4.8; every native
      named resolves in `citizenfx/natives` at a recorded commit; no FXServer build, said so; blocks + bumps

## 3. Probe and pin — Python, TypeScript and browser skills

- [ ] 3.1 `backend-resilience`: the five `python` blocks import and the helpers execute against a stub
      dependency under pinned `httpx`/`structlog` in a venv; block + bump
- [ ] 3.2 `log-event-collector`: the atomic-replace block executes on Python 3.11.2; block + bump
- [ ] 3.3 `api-resilience-testing`: the nine-row baseline table re-measured on `fastapi 0.141.1` /
      `pydantic 2.13.4` in a venv; rows corrected if any differ; block + bump
- [ ] 3.4 `react-api-client`: the three complete `ts` blocks typecheck with pinned `axios`, `zod`,
      `typescript` once given their imports in a probe harness; block + bump
- [ ] 3.5 `svg-animation`: block names Chrome for Testing 151.0.7922.34 and the 2026-08-30/31 runs
      recorded in `research/svg-animation/measurements.md`; block + bump

## 4. Probe and pin — CLI and harness skills

- [ ] 4.1 `openspec` and `openspec-drivezone`: every prescribed subcommand/flag probed on openspec 1.6.0;
      the "strict passes a change missing every gate section" claim re-run in a throwaway project;
      blocks + bumps
- [ ] 4.2 `backlog` and `execute-backlog`: read recipes executed against the AI-SKILLS board on gh
      2.96.0, write recipes' flags checked with `--help`; blocks + bumps
- [ ] 4.3 `code-locale`: `check-identifier-locale.py --selftest` and `locale-rite.py --selftest` on
      Python 3.11.2 under Claude Code 2.1.261; block + bump
- [ ] 4.4 `claude-statusline`: `references/statusline.sh` is byte-identical to the live one and
      rendered under Claude Code 2.1.261 / jq 1.6; fed the sample payload; block + bump
- [ ] 4.5 `conventional-commit`: gitmoji-prefixed subjects released by this repo's pinned
      semantic-release 25 + conventionalcommits 8, evidence from tags/CHANGELOG; block + bump

## 5. Declare — process skills

- [ ] 5.1 `helm-migration`, `bug-hunter`, `documentation`: `**Not version-bound**` sentence with the
      reason; bumps

## 6. Detector and docs

- [ ] 6.1 `check_pin` (C5): literal-phrase rule catalog-wide; declaration exit gated for code-heavy API
      skills; docstring states the new limits and drops the 40-line KNOWN LIMIT
- [ ] 6.2 `selftest-validate-skills.py`: mutations (a) block stripped from a code-heavy skill,
      (b) block reworded to a loose mention, (c) declaration on a code-heavy API skill; old C5 mutation
      removed because its target will carry a block
- [ ] 6.3 README validator paragraph: C5 wording and the selftest count
- [ ] 6.4 `./generate.sh`; wrappers in sync

## 7. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 8. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown

## 9. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate require-verified-against --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive require-verified-against --yes` after all groups above are `[x]`
