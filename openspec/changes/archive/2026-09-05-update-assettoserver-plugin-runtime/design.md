## Context

The doctrine was written against `v0.0.54` (`net8.0`) and the runtime moved to `0.0.55+51d8d8a6e0`
(`net9.0`) without the skill following. `skills/assettoserver-plugin/SKILL.md:38-60` (read
2026-09-05, HEAD 24dcb39) carries the `net8.0` fallback and the `v0.0.54` pin; `:137-151` the
unconditional `System.Threading.Lock` row; `references/publish-pipeline.md:27-32` detects the TFM
from the upstream csproj — which is why a DriveZone build already gets `net9.0` while the text
says `net8.0`. `skills/bug-hunter/references/track-dotnet-plugin.md:22-25` repeats the ban as a
Cecil example.

## Goals / Non-Goals

**Goals:**
- Every version, TFM and package the skill names is read from the tag the production image runs.
- Every forbidden-constructs row states the reason and the host range it holds for.
- A reader upgrading a `v0.0.54`-era plugin sees the plugin-facing surface that moved.
- The catalog gains the general rule: a version-scoped rule moves with the pin.

**Non-Goals:**
- Newest-upstream chasing; editing the DriveZone plugin repo; compiling the real DriveZone plugin.

## Decisions

1. **The `Lock` row is re-scoped, not deleted.** Hosts on `v0.0.54` still exist (the skill's own
   history); the row becomes "on a `net8.0` host (`v0.0.54`) the type is absent — a plugin that must
   load there uses `object`", and the Cecil assert is described as conditional on the detected TFM.
   Alternative — delete the row — rejected: it erases a real incident and the rule the audit change
   wrote about scoping.
2. **The compile probe decides the row, not the reading.** A minimal plugin (Autofac module +
   `ACModuleBase` command + `lock` on `System.Threading.Lock`) is published against the `v0.0.55-pre25`
   tree inside `mcr.microsoft.com/dotnet/sdk:9.0`; the published DLL is checked for the type
   reference and the type is resolved on the .NET 9 runtime. Loading the plugin into the DriveZone
   container is attempted only if the image boots without game content; otherwise the block says the
   load was not observed.
3. **Keep "inherit the TFM, do not hardcode" as DriveZone's rule, and say upstream does the opposite.**
   Upstream's own plugins (`SamplePlugin.csproj`) hardcode `<TargetFramework>net9.0</TargetFramework>`;
   the skill's detection rule is stricter and stays, with the example value corrected.
4. **Drift section, not a changelog.** Only the plugin-facing changes a reader following this skill
   hits; internal renames stay out.
5. **Minor bump** on `assettoserver-plugin`: the doctrine changes (a ban is lifted). **Patch** on
   `bug-hunter`: an example is scoped, no rule changes.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Version pinning of a runtime-bound skill (pin, TFM, packages) | `assettoserver-plugin` (two-contract rule) | already canonical — the bug-hunter track links, does not restate |
| Forbidden-construct inspection method (Cecil on the published DLL) | `bug-hunter` (dotnet track) | already canonical — the plugin skill names the gate and links |
| A version-scoped rule moves with the pin | `skills-authoring` spec (requirement) + `verify-before-claiming` (dated claims) | already canonical — skills carry scoped rows, not the rule |

## Risks / Trade-offs

- [NuGet restore fails in the container] → the probe result is recorded as a failure and the block
  says the compile was not observed; no row is changed on a guess.
- [Lifting the ban breaks a plugin that still loads into `v0.0.54`] → the row stays as a scoped
  note; the Cecil assert is described as conditional on the detected TFM.
- [The drift section goes stale at the next tag] → it is dated and pinned to the two tags it
  compares, like the block.

## Open Questions

- Whether the DriveZone image boots without game content so a plugin load can be observed; if not,
  the load stays unprobed and the block says so.
