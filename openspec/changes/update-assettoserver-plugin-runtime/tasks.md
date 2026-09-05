## 1. Evidence & Sources (MANDATORY)

- [ ] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
- [ ] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
- [ ] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
- [ ] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

## 2. Probe the runtime before writing

- [ ] 2.1 Read the tag: TFM and package versions from `AssettoServer.csproj` at `v0.0.55-pre25`; the
      image's banner and embedded CoreLib version
- [ ] 2.2 Publish a minimal plugin (Autofac module + `ACModuleBase` command + `lock` on
      `System.Threading.Lock`) against the `v0.0.55-pre25` tree in `mcr.microsoft.com/dotnet/sdk:9.0`;
      inspect the published DLL's type references; resolve the type on the .NET 9 runtime
- [ ] 2.3 Attempt to load the published plugin into `drivezone/assettoserver:local`; record what the
      log shows, or that the server did not reach plugin loading
- [ ] 2.4 Diff the plugin-facing surface between `v0.0.54` and `v0.0.55-pre25` and keep only what a
      plugin author hits

## 3. Rewrite the doctrine

- [ ] 3.1 `assettoserver-plugin/SKILL.md`: `Verified against` block, two-contract rule (pin, TFM
      fallback, package versions), forbidden-constructs table with a host range per row, new
      "What moved between v0.0.54 and v0.0.55-pre25" section; minor bump
- [ ] 3.2 `assettoserver-plugin/references/publish-pipeline.md`: checkout-at-the-tag example names
      `v0.0.55-pre25`
- [ ] 3.3 `bug-hunter/references/track-dotnet-plugin.md`: the `System.Threading.Lock` example scoped to
      a `net8.0` host; "type missing in the host" asserts carry the TFM they hold for; patch bump
- [ ] 3.4 `./generate.sh`; wrappers in sync

## 4. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 5. Quality Gates (MANDATORY)

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

## 6. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate update-assettoserver-plugin-runtime --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive update-assettoserver-plugin-runtime --yes` after all groups above are `[x]`
