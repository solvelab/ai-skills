# Change: Re-derive the assettoserver-plugin doctrine for the runtime that actually runs (0.0.55, net9.0)

## Why

`skills/assettoserver-plugin/SKILL.md` pins its doctrine to upstream `v0.0.54`: the two-contract
rule gives `net8.0` as the TFM fallback and the forbidden-constructs table bans `System.Threading.Lock`
because "the pinned runtime is net8.0, so it is absent at load time". The archived change
`2026-08-06-audit-runtime-bound-skills` already called that row version-scoped and said the ban
must be lifted when the pin moves.

The pin moved and the row stayed. Measured on 2026-09-05 (issue #131, PR #144): the DriveZone image
`drivezone/assettoserver:local` reports `AssettoServer 0.0.55+51d8d8a6e0`, built from commit
`51d8d8a6` = tag `v0.0.55-pre25` of `~/works/AssettoServer`, whose `AssettoServer.csproj` targets
`net9.0`; the image's binary embeds `System.Private.CoreLib, Version=9.0.0.0`. On that host the
banned type exists, the `net8.0` example is one major behind, and seven plugin-facing files changed
between the two tags (`Server/Plugin/{ACPluginLoader,AssettoServerModule,AvailablePlugin,
LoadedPlugin,PluginConfiguration}.cs`, `Server/CSPServerScriptProvider.cs`,
`Commands/Attributes/RequireAdminAttribute.cs`; +118/−42). The same ban is replicated as a Cecil
assert example in `skills/bug-hunter/references/track-dotnet-plugin.md`.

## What Changes

- `assettoserver-plugin` (minor bump): pin and `Verified against` block move to `v0.0.55-pre25` /
  `AssettoServer 0.0.55+51d8d8a6e0`; TFM fallback and examples say `net9.0`; package versions read
  from the tag (`Autofac 8.2.0`, `Serilog 4.2.0`, `Qmmands 5.0.2`); the forbidden-constructs table
  carries, per row, the reason and the host range it holds for — the `System.Threading.Lock` row
  becomes a scoped compatibility note for hosts on `net8.0` (`v0.0.54`), not a ban; a new section
  names what moved in the plugin-facing surface between the tags and what it asks of a plugin
  (`AssettoServerModule.ReferenceConfiguration` / `Configure(IApplicationBuilder, IWebHostEnvironment)`,
  `AssettoServerModule<TConfig> where TConfig : new()`, `LoadedPlugin` as `required init` properties
  with `plugin_<snake>_cfg.yml` / schema / reference file names, `ACPluginLoader.LoadPlugins`
  now `internal`, `RequireAdminAttribute` reading `BaseCommandContext.IsAdministrator`).
- `assettoserver-plugin/references/publish-pipeline.md`: the checkout-at-the-runtime's-tag example
  names `v0.0.55-pre25`; the TFM detection stays (it is what already produced the right answer).
- `bug-hunter/references/track-dotnet-plugin.md` (patch bump): the `System.Threading.Lock` example is
  scoped to a `net8.0` host, and the text says every "type missing in the host" assert carries the
  TFM it holds for.
- `skills-authoring`: ADDED requirement **Version-scoped rules move with the pin**.
- No description changes; no skill added or removed; wrappers regenerated.

## Deliberately not done

- Moving to `v0.0.55-pre35` (the newest upstream pre-release): the pin follows the runtime measured
  in production, not the newest tag.
- Touching the DriveZone plugin repository (not on this machine): the skill describes, the repo adopts.
- `assettoserver-ops` (already pinned to `v0.0.55-pre25` by PR #144) and the backend / Lua sections of
  the plugin skill.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED **Version-scoped rules move with the pin** — a rule that holds only for a
  version range names that range, and is lifted or re-scoped in the same change that moves the
  skill's pin out of it.

## Impact

- `skills/assettoserver-plugin/SKILL.md`, `skills/assettoserver-plugin/references/publish-pipeline.md`,
  `skills/bug-hunter/references/track-dotnet-plugin.md`, regenerated wrappers.
- A plugin built by following the corrected skill targets the framework the DriveZone host runs and
  is no longer told to avoid a type that host provides.
