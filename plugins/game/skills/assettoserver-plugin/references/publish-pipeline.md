# AssettoServer plugin — build/publish/verify pipeline

The full rite, in order, as enforced by the production repo's `AGENTS.md`. Every script is bash
with `set -euo pipefail`; each detects `INSIDE_PLUGIN_PUBLISH_CONTAINER=1` to skip its own docker
dispatch when already containerized.

## Rite order (never skip a layer)

```bash
git status --short --branch                      # know your tree before editing
bash -n tooling/scripts/*.sh                     # 1. shell syntax gate
tooling/scripts/run-plugin-tests.sh              # 2. unit tests (host-free)
export ASSETTOSERVER_SOURCE_DIR=~/src/AssettoServer   # checkout at the runtime's tag!
tooling/scripts/build-drivezone-plugin.sh        # 3. compile against upstream
tooling/scripts/publish-drivezone-plugin.sh      # 4. publish (docker by default)
tooling/scripts/run-bug-hunter.sh                # 5. Cecil inspection of the published DLL
tooling/scripts/validate-plugin-repo.sh          # 6. repo hygiene + secret scan
```

A DLL that skipped steps 5–6 must never reach an operational server — the operational repo's sync
script checks for the rite proof (below) before copying.

## Publish script essentials

```bash
# TFM comes from upstream, never hardcoded:
target_framework="$(awk -F'[><]' '/<TargetFramework>/{print $3; exit}' \
  "$ASSETTOSERVER_SOURCE_DIR/AssettoServer/AssettoServer.csproj")"

dotnet publish "$PROJECT_PATH" --configuration Release --output "$OUTPUT_DIR" \
  -p:AssettoServerSourceDir="$ASSETTOSERVER_SOURCE_DIR" \
  -p:TargetFramework="$target_framework"

# Copy upstream third-party deps, excluding host + self:
find "$upstream_build_dir" -maxdepth 1 -type f -name '*.dll' \
  ! -name 'AssettoServer.dll' ! -name 'AssettoServer.Shared.dll' \
  ! -name '<YourPlugin>.dll'

# Fail-fast on incomplete publish:
[[ -f "$OUTPUT_DIR/<YourPlugin>.dll" ]] || fail "publish produced no DLL"
[[ -f "$OUTPUT_DIR/<YourPlugin>.deps.json" ]] || fail "missing .deps.json"
[[ -f "$OUTPUT_DIR/<YourPlugin>.runtimeconfig.json" ]] || fail "missing runtimeconfig"
```

Dispatch policy: default is a reproducible containerized publish
(`docker compose run --rm plugin-publisher`, image = `mcr.microsoft.com/dotnet/sdk:9.0` with the
repo bind-mounted at `/workspace` and the upstream checkout at `/upstream/AssettoServer`);
`USE_HOST_DOTNET=1` is the explicit host-SDK fallback.

## Bug-hunter script + rite proof

Runs the Cecil test project against `PUBLISHED_PLUGIN_DIR`, then writes the proof next to the DLL:

```json
{
  "status": "passed",
  "checked_at_utc": "2026-07-04T18:30:00Z",
  "git_commit": "d864484",
  "published_plugin_dir": ".../artifacts/plugins/<YourPlugin>",
  "bug_hunter": "passed"
}
```

File name: `plugin-rite-status.json`. The operational repo's `sync-*-plugin.sh` refuses to deploy
unless this file exists AND is newer than the DLL — the proof is per-build, not per-repo.

## Repo validation / secret scan

`validate-plugin-repo.sh` enforces:

- required files exist (scripts, sln, AGENTS.md, test csprojs, docker bits);
- **no** `*.dll` / `*.deps.json` / `*.runtimeconfig.json` / `*.log` anywhere outside
  `./artifacts` (prunes `.git`, `obj/`, `bin/`);
- if a publish exists, it has the DLL + deps.json + runtimeconfig triple;
- ripgrep secret sweep — fails on `(?i)(admin_password|password|token|secret)\s*[:=]\s*<value>`
  outside markdown/sln/artifacts/bin/obj. Real tokens live only in the operational repo's
  git-ignored `cfg/`.

## Layout conventions

```
src/<Plugin>/
  Commands/        # ACModuleBase command modules (parameterless ctor!)
  Configuration/   # YAML POCO + best-effort fallback loader
  Hosting/         # AssettoServerModule + IHostedService
  Services/        # feature services (guards, cooldown, backend calls)
  Services/Models/ # chat responses + parsed payload models
  PluginConstants.cs   # every user-facing chat string as a constant
tests/<Plugin>.Tests/                 # host-free unit tests (Compile-linked sources)
tests/<Plugin>.CommandRuntime.Tests/  # real Qmmands instantiation tests
tests/<Plugin>.BugHunter.Tests/       # Mono.Cecil published-DLL inspection
tooling/scripts/  # the six rite scripts
artifacts/plugins/<Plugin>/  # publish output (git-ignored)
```

`Directory.Build.props` stays minimal (`ImplicitUsings`, `Nullable`, `DebugType=embedded`,
`LangVersion=latest`) and deliberately does NOT set `TargetFramework`. `global.json` pins the SDK
(`rollForward: major`).
