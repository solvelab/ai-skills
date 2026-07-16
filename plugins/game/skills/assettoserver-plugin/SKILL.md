---
name: assettoserver-plugin
description: >-
  Conventions for writing C#/.NET plugins for the AssettoServer runtime (compujuckel/AssettoServer,
  the CSP-aware Assetto Corsa dedicated server), distilled from a production DriveZone plugin. Use
  when creating or reviewing an AssettoServer plugin — AssettoServerModule entrypoint, plugin YAML
  config, Qmmands chat commands (ACModuleBase), ChatMessage packets, IHostedService lifecycle,
  calling an external backend from inside the runtime, or publishing for the plugin
  AssemblyLoadContext. Covers the runtime's forbidden constructs (command-module DI,
  System.Threading.Lock) and the bug-hunter gate that enforces them. Do NOT use for stock acServer
  configuration or server operation (that is assettoserver-ops), FiveM/CitizenFX resources (that is
  fivem-lua), or general .NET services.
metadata:
  author: solvelab
  version: 1.2.0
  category: game
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

# AssettoServer plugin conventions

Distilled from a production plugin (DriveZone.AssettoServer.Plugin) that survived real
AssettoServer runtime incompatibilities. Prescriptive: follow these unless the project documents a
deliberate exception. The upstream host is `compujuckel/AssettoServer` — a CSP-aware replacement
for the stock `acServer` with a .NET plugin loader (`EnablePlugins:` in `extra_cfg.yml`).

## The two-contract rule (version pinning)

The plugin is loaded by AssettoServer's `AssemblyLoadContext` into a specific runtime release. It
MUST be compiled against the upstream **source checkout at the exact tag matching that runtime**
(runtime 0.0.54 ↔ upstream tag v0.0.54). Anything else is undefined behavior at load time.

Encode this in the build, don't rely on discipline:

- Do NOT hardcode the TFM — inherit it from upstream:
  `<TargetFramework Condition="'$(TargetFramework)' == ''">net9.0</TargetFramework>` in the csproj,
  and in the publish script detect the real one:
  `awk -F'[><]' '/<TargetFramework>/{print $3; exit}' "$ASSETTOSERVER_SOURCE_DIR/AssettoServer/AssettoServer.csproj"`,
  then pass `-p:TargetFramework="$target_framework"` to `dotnet publish`.
- Add an MSBuild guard target that hard-errors before Restore/Build/Publish when the upstream
  checkout is missing:

```xml
<Target Name="ValidateAssettoServerSourceDir" BeforeTargets="Restore;Build;Publish">
  <Error Condition="'$(AssettoServerSourceDir)' == ''"
         Text="Set -p:AssettoServerSourceDir=... or export ASSETTOSERVER_SOURCE_DIR." />
  <Error Condition="!Exists('$(AssettoServerSourceDir)/AssettoServer/AssettoServer.csproj')"
         Text="AssettoServer.csproj not found under $(AssettoServerSourceDir)." />
</Target>
```

- Reference the host as ProjectReference with `<Private>false</Private>` +
  `<ExcludeAssets>runtime</ExcludeAssets>`: compile against `AssettoServer` and
  `AssettoServer.Shared`, never copy them into the plugin output — the runtime already has them.

## Bootstrap — Autofac module + hosted service

The entrypoint is a class deriving `AssettoServerModule<TConfig>`; the generic parameter is your
YAML config class, deserialized and DI-provided by the host. Register services `SingleInstance`;
do lifecycle work in an `IHostedService`:

```csharp
public sealed class MyPluginModule : AssettoServerModule<MyPluginConfiguration>
{
    protected override void Load(ContainerBuilder builder)
    {
        builder.RegisterType<MyFeatureService>().AsSelf().SingleInstance();
        builder.RegisterType<MyPluginHostedService>()
            .AsSelf().As<IHostedService>().SingleInstance();
    }
}
```

Subscribe host events in `StartAsync`, unsubscribe in `StopAsync`
(`_entryCarManager.ClientConnected += OnClientConnected;`).

## Configuration — YAML POCO, everything disabled by default

- Plain POCO with `[YamlMember(Description = "...")]` on every property and
  `[UsedImplicitly(ImplicitUseKindFlags.Assign, ImplicitUseTargetFlags.WithMembers)]` on the class.
  The host loads it from `cfg/plugin_<snake_case_name>_cfg.yml`.
- **Every feature flag defaults to `false`** (`BackendEnabled = false`, `*Enabled = false`).
  Copying the DLL to a server must never cause visible behavior — enabling is an explicit config
  act, and rollback is "remove the plugin from `EnablePlugins`".
- Timeouts/cooldowns get small safe defaults (timeout 2 s, cooldown 30 s) described in the
  `YamlMember` text — the YAML file is the operator's documentation.
- Keep a best-effort fallback loader for the DI-less path (see forbidden constructs below): probe a
  fixed candidate path list (`/assetto/server/cfg`, `AppContext.BaseDirectory`, cwd), parse flat
  `key: value` lines with `nameof(...)` cases, strip inline `#` comments, and return safe defaults
  on ANY failure. Never let config parsing take the server down.

## Chat & lifecycle

- Send chat only after `ACTcpClient.FirstUpdateSent`, never on `ClientConnected` — at connect time
  the client cannot render chat yet. Subscribe per client, then unsubscribe inside the handler.
- A chat line is a CSP packet: `new ChatMessage { SessionId = 255, Message = ... }` (255 = server),
  sent with `sender.SendPacket(message)` (one client) or
  `_entryCarManager.BroadcastPacket(message, sender)` (everyone).
- One-shot broadcasts are guarded with `Interlocked.Exchange(ref _sent, 1)`; per-player throttles
  use a `ConcurrentDictionary<ulong, DateTimeOffset>` keyed by `sender.Guid`.
- Player identity is `Client.Guid` — the real Steam ID. Skip players with `Guid == 0`.

## Commands — Qmmands ACModuleBase

```csharp
public class MyPluginCommandModule : ACModuleBase
{
    [Command("dzping")]
    public void Ping() => Reply("pong");                 // to the caller only

    [Command("dzbroadcast"), RequireAdmin]
    public void Announce() => Broadcast("message");      // to everyone
}
```

- Admin gate is the `[RequireAdmin]` attribute — never roll your own.
- Multi-line replies: loop `Reply(line)` per line; the backend response is pre-shaped into a
  `Lines` list by the service, the command stays dumb.

## Forbidden constructs (the runtime WILL crash or misbehave)

Qmmands instantiates command modules by reflection, without DI. These three constructs compile
fine and fail only inside the real runtime — enforce them with the bug-hunter gate below:

| Forbidden | Why | Do instead |
|---|---|---|
| `CommandContext.Services` (`get_Services()`) | crashes at command execution | static accessor bridge (below) |
| Command-module constructor with parameters | Qmmands reflects a parameterless ctor; DI never runs | parameterless ctor + accessor |
| `System.Threading.Lock` (C# 13 `lock` on `Lock`) | type missing in the host runtime | `private readonly object _lock = new();` |

**Static accessor bridge** — the sanctioned way to get services into command modules: the
`IHostedService` publishes DI-built singletons into static accessors at `StartAsync`
(`MyServiceAccessor.Set(_service)`); the command calls
`MyServiceAccessor.GetOrCreateFromLocalConfiguration()`, which returns the DI instance or — if DI
never ran — builds one from the fallback YAML loader. All accessor state behind a `lock` on a
plain `object`.

## Calling an external backend from inside the runtime

The game loop is sacred: a chat command must never block or crash the server. The production
doctrine (sibling of the `backend-resilience` skill, adapted to this runtime):

- **Guard order before any I/O**: feature disabled → backend disabled → (identity missing) →
  cooldown active → only then fetch. Each guard returns its own constant chat message.
- **Mark the cooldown BEFORE the request** (`MarkCooldown(); ... await Fetch...`), so a failing
  backend is throttled exactly like a healthy one. Global features use one timestamp under a lock;
  per-player features use a `ConcurrentDictionary<string, DateTimeOffset>`.
- **Short timeout (default 2 s), NO retries, no queues.** A miss shows "temporarily unavailable";
  the next attempt after cooldown is the retry.
- Timeout via `CancellationTokenSource(timeout)` linked to the caller token;
  `catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)` = timeout.
- Inject `TimeProvider` (defaults to `TimeProvider.System`) so cooldowns are testable with a fake.
- **Dual transport**: accept an optional `HttpMessageHandler` through an `internal` constructor —
  when injected (tests) use `HttpClient`; when `null` (real runtime) shell out to `/usr/bin/curl`
  (`--silent --show-error --fail --max-time N --connect-timeout N`, response to a GUID temp file,
  `WaitForExit(timeout)` + `Kill()` fallback, quote/escape URL and token). `HttpClient` has proven
  unreliable inside the AssettoServer runtime; curl is the battle-tested path. Reject non-`http://`
  URLs explicitly.
- **No JSON library.** The production plugin has zero references to `System.Text.Json` or
  Newtonsoft — same assembly-loading risk family as the forbidden constructs. Parse payloads with
  small hand-rolled string scanners (`ReadJsonString`/`ReadJsonInt` helpers, `int.TryParse` with
  `CultureInfo.InvariantCulture`) that throw `FormatException` naming the missing field; tolerate
  `null` where the API allows it (`"top_crasher": null`).
- **Three outcomes, three chat messages** — never collapse failures into one reply: timeout or
  HTTP failure → "temporarily unavailable"; response received but payload malformed
  (`FormatException`) → "invalid data"; HTTP 404 where absence is meaningful → a dedicated typed
  exception (`...ProfileNotFoundException`) → "not found". Not-found is a normal outcome — log it
  `Information`; keep `Warning` for real failures.
- When 404 matters, the curl path must NOT use `--fail` (it eats the status): send the body to
  the temp file and `--write-out "%{http_code}"` to stdout, then branch — `404` → typed
  not-found, any other non-`200` → `HttpRequestException`. Features where 404 can't happen keep
  the plain `--fail` form.
- **Clamp config numbers at the point of use**: `Math.Max(seconds, 0)` when materializing a
  `TimeSpan`, `Math.Max(timeoutSeconds, 1)` for curl `--max-time`/`--connect-timeout`. A nonsense
  YAML value must degrade to a safe one, never throw.
- Auth is a single optional header (e.g. `X-Drivezone-Token`), added only when non-empty. The real
  token lives in the operational repo's git-ignored `cfg/`, never in the plugin repo (the validate
  script secret-scans for `password|token|secret` assignments).
- Sort/limit/tie-break API data **client-side** in the service; over-fetch
  (`Math.Max(limit, 10)`) then trim, so display rules don't depend on backend ordering.

## Serving CSP Lua scripts (configValues + packets)

The plugin can push Lua overlays to every client via `CSPServerScriptProvider.AddScript(script,
debugFilename, configValues)`. The client side of those scripts is `assettoserver-csp-lua`; the
traps below live on THIS side of the boundary:

- **Format every `double` in configValues with `InvariantCulture` yourself.** The provider
  serializes each value with `value.ToString()` — culture-sensitive. On a host with a non-invariant
  locale (`LANG=pt_BR...`), `0.7` becomes `"0,7"`, CSP fails to parse it, and the script silently
  falls back to its Lua defaults. When Lua defaults equal the C# defaults there is **no symptom** —
  the config simply never applies. Ship a helper and use it for every decimal:

  ```csharp
  private static string Decimal(double value) => value.ToString(CultureInfo.InvariantCulture);
  // ["soundVolume"] = Decimal(configuration.SoundVolume),
  ```

- **The flat fallback config loader needs a `case` per property — enforce it with a test, not
  memory.** Commands read config through the DI-less fallback parser (see the static accessor
  bridge above); a property without a `case` silently keeps its default, so the command lies
  ("feature disabled") while the DI path works. This class of bug recurs; kill it with a
  reflection guard that iterates EVERY config property, feeds the parser a YAML line with a
  non-default probe value, and asserts the property changed — then prove the guard works by
  removing one `case` and watching it fail with the property's name.

- **OnlineEvent packet authoring:** server→client pushes need no registration — build the packet
  and `client.SendPacket(packet)`. Client→server packets must be registered via
  `CSPClientMessageTypeManager.RegisterOnlineEvent<TPacket>((client, packet) => ...)`; handlers run
  on the network receive path — hand off to `Task.Run`, never block, never let an exception escape.
  **Never name a packet field `key`**: on the Lua side it collides with the `ac.StructItem.key`
  layout mechanism and the packet is silently never delivered, while every static parity gate
  passes.

## Publish shape (what the plugin loader expects)

```xml
<EnableDynamicLoading>true</EnableDynamicLoading>
<SelfContained>false</SelfContained>
<CopyLocalLockFileAssemblies>true</CopyLocalLockFileAssemblies>
<PublishDir>$(MSBuildThisFileDirectory)..\..\artifacts\plugins\$(MSBuildProjectName)\</PublishDir>
<PathMap>$(MSBuildProjectDirectory)=$(MSBuildProjectName)</PathMap>
```

Publish must yield `<Plugin>.dll` + `.deps.json` + `.runtimeconfig.json`, plus upstream third-party
DLLs copied from the upstream Release build **except** `AssettoServer.dll`,
`AssettoServer.Shared.dll` and the plugin itself. Run the publish inside a pinned SDK container for
reproducibility (scripts detect `INSIDE_PLUGIN_PUBLISH_CONTAINER=1` and skip the docker dispatch).
Full pipeline, scripts and rite order: `references/publish-pipeline.md`.

## Testing — three projects, three purposes

1. **Unit tests** — do NOT reference the host at all. `<Compile Include="..\..\src\...">`-link only
   the service/model sources under test; fake the edges (`StubHttpMessageHandler` returning canned
   JSON, `FakeTimeProvider` with `Advance()`). `InternalsVisibleTo` exposes the internal ctors.
   Cover the adversarial paths: disabled flags, cooldown window, invalid JSON → "invalid data",
   backend 404 → "not found", timeout/HTTP failure → "unavailable".
2. **Command-runtime tests** — reference the real upstream, build a real
   `Qmmands.CommandService`, `AddModules(assembly)`, `ExecuteAsync("dzping", context)` against a
   `FakeCommandContext : BaseCommandContext(null!)` capturing `Replies`/`Broadcasts`. This proves
   commands survive Qmmands' reflection-based instantiation. Skipped when
   `ASSETTOSERVER_SOURCE_DIR` is unset.
3. **Bug-hunter tests** — Mono.Cecil static inspection of the **published DLL**
   (`PUBLISHED_PLUGIN_DIR` env), asserting the forbidden constructs are absent and the publish
   artifacts exist:

```csharp
var methodCalls = assembly.MainModule.GetMemberReferences()
    .Where(m => m.DeclaringType.FullName == "Qmmands.CommandContext")
    .Select(m => m.FullName);
Assert.DoesNotContain("System.IServiceProvider Qmmands.CommandContext::get_Services()", methodCalls);
```

On pass, the bug-hunter script writes `plugin-rite-status.json` (status, UTC timestamp, git short
commit) next to the DLL — the deploy side refuses to sync a DLL without a rite proof newer than it
(see `assettoserver-ops`). Test naming: `Method_describes_behavior_in_snake_case`.

## See also

- `assettoserver-csp-lua` — the client side of the scripts and packets this plugin serves: render
  doctrine, DirectWrite traps, packet layout mirroring, remote assets/audio by URL.
- `assettoserver-ops` — operating the server that loads this plugin; the deploy/sync gate that
  consumes `plugin-rite-status.json`.
- `bug-hunter` — the adversarial rite; `references/track-dotnet-plugin.md` is the generalized
  version of the Mono.Cecil published-artifact inspection.
- `backend-resilience` — the fallback doctrine the backend-call section adapts to this runtime.
- `conventional-commit` — commit format used by this repo.
