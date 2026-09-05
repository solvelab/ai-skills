## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
      Evidence: Opened 2026-09-05 at HEAD 7709622: `scripts/validate-skills.py:244-266` (C5, PIN/API_HINT), `scripts/selftest-validate-skills.py:30-31` (the C5 mutation), `openspec/specs/skills-authoring/spec.md:265-293` (the requirement), `README.md:875-913`, `openspec/changes/archive/2026-08-06-pin-probed-skills/{proposal,tasks}.md` (the precedent), the 20 `skills/<name>/SKILL.md` and `skills/react-api-client/references/api-client.md`, `skills/api-resilience-testing/references/negative-test-catalog.md:98-108`, `skills/svg-animation/references/platform.md:4-8`, `research/svg-animation/measurements.md:9-40`, `.releaserc.json`, `.github/workflows/ci.yml`. Outside the repo, read the same day: `~/works/AssettoServer` at tag `v0.0.55-pre25` (commit 51d8d8a6), `~/.claude/settings.json:26-50`, `~/.claude/statusline.sh`.
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
      Evidence: `grep -L 'Verified against\|does not depend on a tool version' skills/*/SKILL.md | wc -l` -> `20` before, `0` after. `docker run --rm --entrypoint sh drivezone/assettoserver:local -c './AssettoServer --version'` -> `AssettoServer 0.0.55+51d8d8a6e0`. `git show v0.0.54:AssettoServer/AssettoServer.csproj | grep TargetFramework` -> `net8.0`; HEAD -> `net9.0`. 15/15 `extra_cfg.yml` keys and 24/25 `server_cfg.ini` keys resolve in the clone (`CARS` never read). `git clone --depth 1 acc-lua-sdk` @ 7cf60f5a -> 12/15 CSP names declared (`ui.measureDWriteText`, `ui.pushDWriteFont`, `ac.onCarCollision` absent). `docker run nickblah/lua:5.4-luarocks luac -p` over 14 Lua files -> `ok=13 bad=1` (the marked excerpt). citizenfx/fivem @ 6fd665a3 + natives @ 7263f211 -> 12/12 runtime functions resolve. venv: `fastapi 0.141.1 pydantic 2.13.4 starlette 1.6.0 httpx 0.28.1 structlog 26.1.0 prometheus_client 0.26.0 uvicorn 0.52.4`; baseline table -> 8/9 rows held, nested brackets -> `400 {"detail":"There was an error parsing the body"}` at 990/1000/1500/10000 levels under TestClient and uvicorn. backend-resilience blocks executed -> `safe_call fail -> (False, -1)`, counter `1.0`, `retry -> ok attempts 3`, negative cache `upstream calls 1`. `npx tsc -p` on react-api-client blocks -> 24 errors as written (`typescript 7.0.2`, `axios 1.20.0`, `zustand 5.0.15`). `openspec <cmd> --help` -> 11/11 subcommands, 5/5 flags; throwaway `openspec validate probe --strict` -> `Change 'probe' is valid` with no gate group. `gh <cmd> --help` -> `ok=58 fail=0` flags over 18 subcommands on `gh 2.96.0`. `check-identifier-locale.py --selftest`, `locale-rite.py --selftest`, `locale-stop-gate.py --selftest` -> all `selftest OK` on Python 3.11.2. `statusline.sh` fed a synthetic payload -> three rendered lines, `exit=0`; `diff -q ~/.claude/statusline.sh skills/claude-statusline/references/statusline.sh` -> identical. `git log -1 --format=%cs v2.24.0` -> 2026-09-05 from `✨ feat(code-locale)`.
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
      Evidence: Not probed, and written into the blocks as such: the CSP client and the CSP build the DriveZone servers require (no config on this machine; the server image carries no `extra_cfg.yml`); the three CSP names absent from the SDK tree; any FXServer build; the DriveZone repositories behind `openspec-drivezone`; the project `react-api-client` was extracted from; a compiled plugin against AssettoServer (dotnet SDK 9 image exists, the build was not attempted — cost, and the pin is declared as a source read); the live status-line payload field by field; Chrome for Testing (the svg numbers are the 2026-08-30/31 runs). Open question kept from design.md: the CSP build number, left as an explicit gap.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed
      Evidence: Follow-ups noticed and NOT performed: (1) `assettoserver-plugin` doctrine (`net8.0` fallback, `System.Threading.Lock` ban) re-derived for the `0.0.55+51d8d8a6e0` runtime that targets `net9.0` — the block discloses it; (2) `python-rest-api` SKILL.md:103 publishes the same `500 (RecursionError)` row that did not reproduce (measured 400) — outside this item's 20 skills; (3) C5 does not check the date inside the block; enforcing it needs the 15 pre-existing blocks backfilled from their archived changes; (4) `react-api-client` blocks rewritten to compile instead of being marked excerpts; (5) `openspec spec list` deprecation on 1.6.0 — move the two openspec skills to `openspec show` / `validate --specs` when the pin moves; (6) README still says `C1–C9` in the tree listing at line 468 (stale before this change).
## 2. Probe and pin — game and server skills (AssettoServer clone, DriveZone image, public stubs)

- [x] 2.1 `assettoserver-ops`: every `extra_cfg.yml` key and the density function it quotes resolve in
      `~/works/AssettoServer` at `v0.0.55-pre25`; the DriveZone image reports its version; block + bump
      Evidence: 15/15 `extra_cfg.yml` keys -> `Server/Configuration/Extra/AiParams.cs` etc.; 24/25 ini keys; `AiBehavior.cs:455-466` matches the quoted function; image -> `AssettoServer 0.0.55+51d8d8a6e0`. `skills/assettoserver-ops/SKILL.md` 1.3.0 -> 1.3.1.
- [x] 2.2 `assettoserver-plugin`: TFM and package versions at `v0.0.54` read from the clone; the
      `0.0.55+51d8d8a6e0` / `net9.0` contradiction disclosed in the block; block + bump
      Evidence: `git show v0.0.54:...csproj` -> `net8.0`, `Qmmands 5.0.2`, `Autofac 7.1.0`, `Serilog 3.1.1`; `AssettoServerModule`, `ACModuleBase` declared at v0.0.54; `Commands/Attributes/RequireConnectedPlayerAttribute.cs` present; `System.Threading.Lock` used nowhere at HEAD. Block discloses `net9.0` at HEAD. 1.3.2 -> 1.3.3.
- [x] 2.3 `assettoserver-csp-lua`: the 15 `ac.*`/`ui.*` names resolve in `acc-lua-sdk` at a recorded
      commit; `snippets.lua` parses on Lua 5.4.8; in-game behaviour named as not probed; block + bump
      Evidence: acc-lua-sdk @ 7cf60f5a: 12/15 declared (`common/ac_ui.lua`, `common/ac_extras_onlineevent.lua`, `ac_online_script.lua`, `lib_audio.lua`…); `luac -p references/snippets.lua` ok; `CSPServerScriptProvider.cs:65` `AddScript(string script, string? debugFilename, Dictionary<string, object>? configuration)`, `:77` `SCRIPT_{10 + Scripts.Count}-{debugFilename}`, `:101` `/api/scripts/{Scripts.Count}`. 1.1.1 -> 1.1.2.
- [x] 2.4 `fivem-lua` and `fivem-fallback`: every fenced Lua block parses on Lua 5.4.8; every native
      named resolves in `citizenfx/natives` at a recorded commit; no FXServer build, said so; blocks + bumps
      Evidence: `luac -p` (Lua 5.4.8): fivem-lua 6/7 parse + 1 marked excerpt (`events-registry.md` block 1, `...` placeholder), fivem-fallback 5/5. `ext/native-decls/{RegisterNuiCallbackType,SetNuiFocus,SendNuiMessage,GetConvar,GetGameTimer,TriggerClientEventInternal,PerformHttpRequestInternal}.md` and `scheduler.lua` (`RegisterNetEvent`, `CreateThread`, `Wait`, `SetTimeout`, `AddEventHandler`) at fivem 6fd665a3. fivem-lua 1.3.2 -> 1.3.3, fivem-fallback 1.3.0 -> 1.3.1.
## 3. Probe and pin — Python, TypeScript and browser skills

- [x] 3.1 `backend-resilience`: the five `python` blocks import and the helpers execute against a stub
      dependency under pinned `httpx`/`structlog` in a venv; block + bump
      Evidence: `venv/bin/python run_backend.py` -> `block0 httpx.Timeout -> Timeout(connect=1.0, read=2.0, write=2.0, pool=1.0)`, `safe_call fail -> (False, -1)`, `safe_call_async fail -> (False, -2)`, `clamp_num -> 5 3 3 2.5`, counter sample `1.0`, `retry -> ok attempts 3`, `deadline -> deadline attempts 0`, `first -> None second -> None upstream calls 1`, `cfg -> {'xp_per_level': 100, 'max_level': 50}`. 2.0.1 -> 2.0.2.
- [x] 3.2 `log-event-collector`: the atomic-replace block executes on Python 3.11.2; block + bump
      Evidence: `venv/bin/python run_lec.py` -> `first read -> ['line one', 'line two'] offset 18`, `second read -> ['partial tail', 'line four'] offset 41`; atomic replace -> `{'offset': 123} tmp left: False`. 1.1.0 -> 1.1.1.
- [x] 3.3 `api-resilience-testing`: the nine-row baseline table re-measured on `fastapi 0.141.1` /
      `pydantic 2.13.4` in a venv; rows corrected if any differ; block + bump
      Evidence: `baseline.py` under TestClient and `nested_uvicorn.py` under uvicorn 0.52.4 -> 422/422/422/200/422/405(Allow=GET)/200/**400**/200; `fastapi/routing.py:469-473` is the `except Exception -> HTTPException(400, "There was an error parsing the body")` that catches the `RecursionError`. Row, prose (SKILL.md:181-186) and `references/negative-test-catalog.md:103-108` corrected to 400. 1.3.1 -> 1.3.2.
- [x] 3.4 `react-api-client`: the three complete `ts` blocks typecheck with pinned `axios`, `zod`,
      `typescript` once given their imports in a probe harness; block + bump
      Evidence: `npx tsc -p tsconfig.json` (typescript 7.0.2, axios 1.20.0, zustand 5.0.15 from package-lock) -> 24 errors across the three complete-looking blocks as written; harness with imports + declarations still fails (elided constructors, `original.headers.set` on the config union). Three blocks now open with `// excerpt — condensed: …`; the fourth already did. 1.1.1 -> 1.1.2.
- [x] 3.5 `svg-animation`: block names Chrome for Testing 151.0.7922.34 and the 2026-08-30/31 runs
      recorded in `research/svg-animation/measurements.md`; block + bump
      Evidence: `research/svg-animation/measurements.md:11` -> `Google Chrome for Testing 151.0.7922.34, headless (--headless=new)`, `:39` -> `measured on 2026-08-30`, `:181` -> second run 2026-08-31; `references/platform.md:6` names the same build. Block cites both files by repository URL (C12). 1.1.2 -> 1.1.3.
## 4. Probe and pin — CLI and harness skills

- [x] 4.1 `openspec` and `openspec-drivezone`: every prescribed subcommand/flag probed on openspec 1.6.0;
      the "strict passes a change missing every gate section" claim re-run in a throwaway project;
      blocks + bumps
      Evidence: `openspec --version` -> 1.6.0; 11/11 subcommands `--help` exit 0; `validate --help` lists `--all --type --strict --no-interactive`; `spec list --help` lists `--long` and the run prints `Warning: The "openspec spec ..." commands are deprecated`; throwaway `openspec init --tools none` + change with `tasks.md` = one plain group -> `openspec validate probe --strict` -> `Change 'probe' is valid`. openspec 1.1.1 -> 1.1.2, openspec-drivezone 2.1.3 -> 2.1.4.
- [x] 4.2 `backlog` and `execute-backlog`: read recipes executed against the AI-SKILLS board on gh
      2.96.0, write recipes' flags checked with `--help`; blocks + bumps
      Evidence: `gh --version` -> 2.96.0; `gh-flags.txt` -> `ok=58 fail=0`; live: `gh project item-list 3 --owner solvelab --limit 200 --format json --jq` -> item id, `gh project field-list` -> Status options, `gh project item-edit ... --single-select-option-id 61e4505c` then `47fc9ee4` moved #131 Backlog -> Ready -> In progress, `gh api repos/solvelab/ai-skills/issues/131/timeline --jq` -> 1 cross-reference, `gh issue view 131 --json closedByPullRequestsReferences` -> 0. backlog 1.5.1 -> 1.5.2, execute-backlog 1.8.2 -> 1.8.3.
- [x] 4.3 `code-locale`: `check-identifier-locale.py --selftest` and `locale-rite.py --selftest` on
      Python 3.11.2 under Claude Code 2.1.261; block + bump
      Evidence: `python3 skills/code-locale/references/check-identifier-locale.py --selftest` -> `selftest OK: 7 content tiers fire, 16 clean cases stay silent, 6 path tiers fire, 9 path cases stay silent, 2 en-unknown tiers fire, 5 en-unknown cases stay silent`; `locale-rite.py --selftest` -> `13 PostToolUse decisions, 12 PreToolUse decisions`; `locale-stop-gate.py --selftest` -> `26 decisions`; `~/.claude/settings.json:26,38,49` wire both hooks. 1.4.0 -> 1.4.1.
- [x] 4.4 `claude-statusline`: `references/statusline.sh` is byte-identical to the live one and
      rendered under Claude Code 2.1.261 / jq 1.6; fed the sample payload; block + bump
      Evidence: `diff -q ~/.claude/statusline.sh skills/claude-statusline/references/statusline.sh` -> identical; `printf '<payload>' | bash references/statusline.sh` -> `🤖 Fable 5.1 | ⚡ medium | 🧠 thinking enabled | ⏱️ 1m 5s | 💰 $1.23` + two more lines, `exit=0`; `claude --version` -> 2.1.261, `jq --version` -> jq-1.6, bash 5.2.15. 1.2.1 -> 1.2.2.
- [x] 4.5 `conventional-commit`: gitmoji-prefixed subjects released by this repo's pinned
      semantic-release 25 + conventionalcommits 8, evidence from tags/CHANGELOG; block + bump
      Evidence: `.releaserc.json` headerPattern `^(?:[^\w\s]+\s+)?(\w+)(?:\((.*)\))?!?: (.*)$`; `ci.yml:279` installs `semantic-release@25 ... conventional-changelog-conventionalcommits@8`; `git log -1 --format=%cs v2.24.0` -> 2026-09-05 <- `✨ feat(code-locale)` (b1f527f); v2.23.0 <- 69aaf73; v2.22.0 <- 49c44d0. 1.3.1 -> 1.3.2.
## 5. Declare — process skills

- [x] 5.1 `helm-migration`, `bug-hunter`, `documentation`: `**Not version-bound**` sentence with the
      reason; bumps
      Evidence: `grep -c -i -E 'helm |kubectl' skills/helm-migration/SKILL.md` restricted to commands -> 0 prescribed commands; bug-hunter tracks name `pytest`, `busted`, Cecil with no version flag; documentation prescribes no CLI. Blocks written with the literal `does not depend on a tool version`. helm-migration 2.2.2 -> 2.2.3, bug-hunter 2.2.2 -> 2.2.3, documentation 3.0.2 -> 3.0.3.
## 6. Detector and docs

- [x] 6.1 `check_pin` (C5): literal-phrase rule catalog-wide; declaration exit gated for code-heavy API
      skills; docstring states the new limits and drops the 40-line KNOWN LIMIT
      Evidence: `scripts/validate-skills.py` C5: `PIN = re.compile(r"Verified against")`, `NO_VERSION`, `DEFERS`; finding text `neither 'Verified against' nor 'does not depend on a tool version' — a version mentioned in passing is not a pin` / `N lines of code against a versioned API, declared not version-bound`; docstring header line updated; `python3 scripts/validate-skills.py` -> `skills checked: 35   findings: 0`.
- [x] 6.2 `selftest-validate-skills.py`: mutations (a) block stripped from a code-heavy skill,
      (b) block reworded to a loose mention, (c) declaration on a code-heavy API skill; old C5 mutation
      removed because its target will carry a block
      Evidence: `scripts/selftest-validate-skills.py`: mutations `C5 no version pin` (fivem-lua, literal stripped), `C5 no version pin (loose mention)` (openspec, `Probed on CLI 1.6.0` left in place), `C5 no version pin (declaration on code-heavy API skill)` (k8s-tune-resources, 73 fenced lines, `kubectl` hint); run -> `CAUGHT` for all three, `21/22 defect classes detected` locally — the one MISSED is the pre-existing `C3 lua syntax` (luac not installed here; CI installs lua5.4).
- [x] 6.3 README validator paragraph: C5 wording and the selftest count
      Evidence: `README.md:878-879` -> `every skill states what it was verified against or that it does not depend on a tool version (C5)`; `:913` -> `22/22 defect classes detected` (was a stale `13/13` against a selftest that already had 20).
- [x] 6.4 `./generate.sh`; wrappers in sync
      Evidence: `bash generate.sh` then `git status --porcelain --untracked-files=all | grep -c '^??'` -> 0; the generated trees change only where `skills/` changed (87 paths in the working tree before commit).
## 7. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
      Evidence: entry point `python3 scripts/validate-skills.py` on the catalog -> `skills checked: 35   findings: 0`; on a copy with the literal stripped from `skills/fivem-lua/SKILL.md` -> `C5 no version pin      1` and, under `fivem-lua`, `[C5 no version pin] neither 'Verified against' nor 'does not depend on a tool version' — a version mentioned in passing is not a pin`. entry point `python3 scripts/selftest-validate-skills.py` -> `CAUGHT  C5 no version pin`, `CAUGHT  C5 no version pin (loose mention)`, `CAUGHT  C5 no version pin (declaration on code-heavy API skill)`, `21/22 defect classes detected`.
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
      Evidence: 3/3 C5 mutations had to fire and did; 35/35 skills had to stay silent and did (`findings: 0`); 20/20 new blocks carry `2026-09-05`; 1/1 known escape stayed silent — `helm-migration` (82 fenced yaml lines, `helm ` in prose, the declaration) passes through the deferral phrase it already carries, by design; 1/1 pre-existing local miss unchanged — `C3 lua syntax` (luac absent here, installed by CI).
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did
      Evidence: Four things behaved differently than expected and were acted on: (1) mutation (c) on `r3f-materials` stayed silent because its SKILL.md has 0 fenced lines (code lives under references/) — retargeted to `k8s-tune-resources`; (2) the svg-animation block tripped C12 on two `research/…` paths — replaced by repository URLs; (3) the api-resilience-testing nested-brackets row did not reproduce (400, not 500) on the very stack it names — corrected in three places and disclosed in the block; (4) the GitHub code-search endpoint rate-limited the first CSP/natives probe (10/min) — redone with shallow clones, which is also the more reproducible evidence.
## 8. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      Evidence: CI frontmatter loop replicated locally over `skills/*/SKILL.md` -> `frontmatter fail=0`; `agentskills validate` (skills-ref 0.1.1) -> `fail=0 over 35 skills`; `npx -y @anthropic-ai/claude-code@2.1.246 plugin validate . --strict` -> `✔ Validation passed`.
- [x] Q.2 All touched skill content in English (catalog locale)
      Evidence: Every block and every corrected line is English; `python3 skills/code-locale/references/check-identifier-locale.py <23 changed canonical files>` -> `findings: 0` (4 en-unknown segments, advisory).
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Evidence: `git diff master -- skills/ | grep -E '^[-+]\s*description' | wc -l` -> `0`: no description changed, so no trigger or boundary moved.
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Evidence: The blocks state what was probed and link nothing restated; the probing doctrine stays in `verify-before-claiming`, the requirement in `skills-authoring`, the rule in C5's docstring (design.md Canonical Home table, three rows, all `already canonical`).
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown
      Evidence: No code example was added; the detector run in Q.2 covers the 22 changed skill files -> `findings: 0`.
## 9. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate require-verified-against --strict` green
      Evidence: `openspec validate require-verified-against --strict` -> `Change 'require-verified-against' is valid`; `bash scripts/validate-rite.sh` -> `rite gate OK` (evidence gate 0 findings, spec-rite gate 0 findings).
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
      Evidence: `npx -y skills add solvelab/ai-skills --list | grep -c -E '^│    [a-z0-9-]+$'` -> `35`, the tree count; no skill added, removed or renamed.
- [x] V.3 README / docs updated where the change alters catalog composition or usage
      Evidence: `README.md:878-879` C5 wording and `:913` selftest count updated; catalog composition unchanged, so no other doc moves.
- [ ] V.4 `openspec archive require-verified-against --yes` after all groups above are `[x]`
