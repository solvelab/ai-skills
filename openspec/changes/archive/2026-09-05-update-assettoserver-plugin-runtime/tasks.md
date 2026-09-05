## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
      Evidence: Opened 2026-09-05 at HEAD 24dcb39: `skills/assettoserver-plugin/SKILL.md:23-60,137-160,237-262`, `skills/assettoserver-plugin/references/publish-pipeline.md` (whole), `skills/bug-hunter/references/track-dotnet-plugin.md:1-50`, `openspec/changes/archive/2026-08-06-audit-runtime-bound-skills/proposal.md`, `.github/backlog.yml`. Outside the repo the same day: `~/works/AssettoServer` at `v0.0.55-pre25` (commit 51d8d8a6) — `AssettoServer/AssettoServer.csproj`, `AssettoServer/Server/Plugin/{AssettoServerModule,LoadedPlugin,ACPluginLoader,AvailablePlugin,PluginConfiguration}.cs`, `AssettoServer/Commands/Attributes/RequireAdminAttribute.cs`, `AssettoServer/Server/CSPServerScriptProvider.cs`, `SamplePlugin/SamplePlugin.csproj`, `global.json`; the image's `/assetto/scripts/start-server.sh`.
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
      Evidence: `git show v0.0.55-pre25:AssettoServer/AssettoServer.csproj | grep -E 'TargetFramework|Autofac|Serilog|Qmmands'` -> `net9.0`, `Autofac 8.2.0`, `Serilog 4.2.0`, `Qmmands 5.0.2`; `git show v0.0.54:...csproj` -> `net8.0`, `Autofac 7.1.0`, `Serilog 3.1.1`. `docker run --rm --entrypoint sh drivezone/assettoserver:local -c './AssettoServer --version'` -> `AssettoServer 0.0.55+51d8d8a6e0`; `grep -a -o 'System.Private.CoreLib, Version=[0-9.]*' AssettoServer` -> CoreLib 9.0. `docker run mcr.microsoft.com/dotnet/sdk:9.0 dotnet publish ProbePlugin -c Release` -> `publish exit=0`, `real 0m28.596s`, `ProbePlugin.deps.json ProbePlugin.dll ProbePlugin.runtimeconfig.json`, `"tfm": "net9.0"`, `no host assemblies copied`. System.Reflection.Metadata over the DLL -> `type references: 31`, `System.Threading.Lock`, `AssettoServer.Commands.ACModuleBase`, `AssettoServer.Server.Plugin.AssettoServerModule`1`; `assembly references: System.Runtime 9.0, AssettoServer (unversioned), Qmmands 5.0.2, Autofac 8.2, Microsoft.Extensions.Hosting.Abstractions 9.0`. `dotnet run` of `typeof(System.Threading.Lock).Assembly.FullName` on the 9.0 runtime -> `System.Private.CoreLib 9.0`. Load: `docker run -w /assetto/server --entrypoint /assetto/assettoserver/AssettoServer drivezone/assettoserver:local` with `cfg/extra_cfg.yml: EnablePlugins: [ProbePlugin]` -> `[INF] Loaded plugin ProbePlugin`, `[INF] Starting server`, then `ConfigurationException: No data.acd found for abarth500`. `git diff --stat v0.0.54 HEAD -- AssettoServer/Server/Plugin AssettoServer/Commands/ACModuleBase.cs AssettoServer/Commands/Attributes AssettoServer/Server/CSPServerScriptProvider.cs` -> `7 files changed, 118 insertions(+), 42 deletions(-)`, `ACModuleBase.cs` absent from the stat. `git ls-remote --tags origin 'v0.0.55*'` -> newest `v0.0.55-pre35`, no final.
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
      Evidence: Not probed and written as such: a chat command executed in game (the server stopped on missing content right after loading the plugin — `Loaded plugin ProbePlugin` is the observed boundary); the real DriveZone plugin repository (not on this machine); every plugin-facing change listed in the drift section is read from the diff, not exercised against a plugin that uses it. The image's own `start-server.sh` never reaches plugin loading without game content (`[validate-config] Config validation failed with 10 error(s)`), so the load was observed by running the binary directly.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed
      Evidence: Follow-ups noticed and NOT performed: (1) the `assettoserver-plugin` description still lists `System.Threading.Lock` among the forbidden constructs it covers — now a scoped row; a description edit is a trigger change and stays out of this item; (2) the server at `v0.0.55-pre25` logs `Using minimum required CSP Version 1937` with a default `extra_cfg.yml` — a number the open CSP-build gap in `assettoserver-csp-lua` can use; (3) NuGet reports `Scriban 6.0.0` vulnerabilities (NU1902-NU1904) while restoring the upstream tree — upstream's dependency, not the skill's; (4) the `require-verified-against` change (#131) is still active pending its archive PR; (5) upstream is at `v0.0.55-pre35` — the pin follows the runtime, not the newest tag, by scope.
## 2. Probe the runtime before writing

- [x] 2.1 Read the tag: TFM and package versions from `AssettoServer.csproj` at `v0.0.55-pre25`; the
      image's banner and embedded CoreLib version
      Evidence: `git show v0.0.55-pre25:AssettoServer/AssettoServer.csproj` -> `<TargetFramework>net9.0</TargetFramework>`, `Autofac 8.2.0`, `Serilog 4.2.0`, `Qmmands 5.0.2`; image banner `AssettoServer 0.0.55+51d8d8a6e0`; embedded CoreLib 9.0.
- [x] 2.2 Publish a minimal plugin (Autofac module + `ACModuleBase` command + `lock` on
      `System.Threading.Lock`) against the `v0.0.55-pre25` tree in `mcr.microsoft.com/dotnet/sdk:9.0`;
      inspect the published DLL's type references; resolve the type on the .NET 9 runtime
      Evidence: `dotnet publish` in `mcr.microsoft.com/dotnet/sdk:9.0` (SDK 9.0.315) -> exit 0, 28.6 s, triple present, `tfm net9.0`, no host assembly; metadata reader -> `System.Threading.Lock` among 31 type references; `typeof(System.Threading.Lock)` resolves to CoreLib 9.0 on the runtime.
- [x] 2.3 Attempt to load the published plugin into `drivezone/assettoserver:local`; record what the
      log shows, or that the server did not reach plugin loading
      Evidence: Binary run directly with `EnablePlugins: [ProbePlugin]` -> `[INF] Loaded plugin ProbePlugin` then `[INF] Starting server`; hosting stopped on `No data.acd found for abarth500` (missing game content, expected). The image's start script itself refused to launch without content (`Config validation failed with 10 error(s)`).
- [x] 2.4 Diff the plugin-facing surface between `v0.0.54` and `v0.0.55-pre25` and keep only what a
      plugin author hits
      Evidence: 7 files; kept: `AssettoServerModule` (`ReferenceConfiguration`, `Configure(IApplicationBuilder, IWebHostEnvironment)`, `where TConfig : new()`), `LoadedPlugin` (`required init`, `Directory`, `plugin_<snake>_cfg.yml`/`.schema.json`/`.reference.yml`), `ACPluginLoader.LoadPlugins` internal, `RequireAdminAttribute` -> `BaseCommandContext { IsAdministrator: true }`, `CSPServerScriptProvider` ctor + `OnExtraOptionsSending`; dropped: `List<> = []` style, `Path` renames. `ACModuleBase` unchanged.
## 3. Rewrite the doctrine

- [x] 3.1 `assettoserver-plugin/SKILL.md`: `Verified against` block, two-contract rule (pin, TFM
      fallback, package versions), forbidden-constructs table with a host range per row, new
      "What moved between v0.0.54 and v0.0.55-pre25" section; minor bump
      Evidence: `skills/assettoserver-plugin/SKILL.md`: block rewritten (`grep -c 'Verified against'` -> 1), two-contract rule names `v0.0.55-pre25 ↔ 0.0.55+51d8d8a6e0` and `net9.0`, table gained a `Host range` column with the `Lock` row scoped to `v0.0.54`/`net8.0`, new section `## What moved between v0.0.54 and v0.0.55-pre25 (plugin-facing)`; `grep -n net8.0` -> 5 lines, every one about the `v0.0.54` host. `version: 1.3.3 -> 1.4.0`.
- [x] 3.2 `assettoserver-plugin/references/publish-pipeline.md`: checkout-at-the-tag example names
      `v0.0.55-pre25`
      Evidence: `references/publish-pipeline.md:15` -> `checkout at the runtime's tag (v0.0.55-pre25 for 0.0.55+51d8d8a6e0)`; `:26` -> `reads net9.0 at v0.0.55-pre25, net8.0 at v0.0.54`.
- [x] 3.3 `bug-hunter/references/track-dotnet-plugin.md`: the `System.Threading.Lock` example scoped to
      a `net8.0` host; "type missing in the host" asserts carry the TFM they hold for; patch bump
      Evidence: `skills/bug-hunter/references/track-dotnet-plugin.md:22-29`: `System.Threading.Lock` example prefixed `only for a host on net8.0 (AssettoServer v0.0.54)`, sentence added: an assert whose reason is a missing host type carries the TFM it holds for and reads the detected TFM before firing. `skills/bug-hunter/SKILL.md` `version: 2.2.3 -> 2.2.4`.
- [x] 3.4 `./generate.sh`; wrappers in sync
      Evidence: `bash generate.sh` -> `git status --porcelain --untracked-files=all | grep -c '^??'` -> 0; 11 paths changed before commit (3 canonical + wrappers + tasks).
## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
      Evidence: entry point `dotnet publish ProbePlugin/ProbePlugin.csproj -c Release` (SDK 9.0.315, tree at v0.0.55-pre25) -> `publish exit=0`; entry point `/assetto/assettoserver/AssettoServer` in `drivezone/assettoserver:local` with the published plugin mounted under `plugins/ProbePlugin` -> `[INF] Loaded plugin ProbePlugin`; entry point `python3 scripts/validate-skills.py` on the rewritten catalog -> `skills checked: 35   findings: 0`.
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
      Evidence: 1/1 plugin using `System.Threading.Lock` had to compile against the net9.0 tree and did; 1/1 had to be loaded by the DriveZone runtime and was; 1/1 type reference had to appear in the published DLL and did (31 type refs, `System.Threading.Lock` present); 3/3 files of the publish triple present, 0/0 host assemblies copied; 35/35 skills silent on C5/C4/C12 after the rewrite; 0/1 in-game command executed (server stopped on content before any client could connect — known, recorded).
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did
      Evidence: Two things behaved differently than expected: (1) `grep -a -c System.Threading.Lock ProbePlugin.dll` -> 0 although the type is referenced — metadata stores namespace and name as separate heap strings, so the byte grep was replaced by a System.Reflection.Metadata reader; the Cecil `GetTypeReferences()` approach the track prescribes is the right one and a `grep` on the DLL is not; (2) the image's `start-server.sh` validates game content before launching and never reaches plugin loading — the load was observed by running the binary directly with the same cfg. Also: `scan-secrets.py` flagged the dotted four-part CoreLib version string as a public IPv4 — reworded to `CoreLib 9.0`.
## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      Evidence: Frontmatter loop replicated over `skills/*/SKILL.md` -> `frontmatter fail=0`; `agentskills validate` -> `fail=0` over 35; `npx -y @anthropic-ai/claude-code@2.1.246 plugin validate . --strict` -> `✔ Validation passed`.
- [x] Q.2 All touched skill content in English (catalog locale)
      Evidence: All rewritten text is English; `check-identifier-locale.py` over the changed `skills/` files -> `findings: 0`.
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Evidence: `git diff master -- skills/ | grep -c -E '^[-+]\s*description'` -> `0`; no trigger moved. The description's mention of `System.Threading.Lock` as a covered forbidden construct is recorded in E.4 as a follow-up, not edited here.
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Evidence: The bug-hunter track links the plugin skill for the scoped row instead of restating the runtime facts; the plugin skill names the Cecil gate and links the track; the new spec requirement lives in `skills-authoring` only (design.md Canonical Home, three rows, all `already canonical`).
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown
      Evidence: No new code example; the one XML/C# fragment touched (`<TargetFramework …>net9.0`) is an identifier-free value change; detector -> `findings: 0`.
## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate update-assettoserver-plugin-runtime --strict` green
      Evidence: `openspec validate update-assettoserver-plugin-runtime --strict` -> `Change 'update-assettoserver-plugin-runtime' is valid`; `bash scripts/validate-rite.sh` -> `rite gate OK` (evidence gate 0, spec-rite gate 0 with 2 active changes).
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
      Evidence: No skill added, removed or renamed; `npx -y skills add solvelab/ai-skills --list` counted 35 earlier the same day and the tree still holds 35 (`ls skills | wc -l`).
- [x] V.3 README / docs updated where the change alters catalog composition or usage
      Evidence: No catalog composition or usage change; README untouched on purpose.
- [x] V.4 `openspec archive update-assettoserver-plugin-runtime --yes` after all groups above are `[x]`
      Evidence: `openspec archive update-assettoserver-plugin-runtime --yes` on 2026-09-05 after PR merge -> archived as `2026-09-05-update-assettoserver-plugin-runtime`, specs updated; `openspec list` -> `No active changes found`.