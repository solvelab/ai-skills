# Track — .NET plugin loaded by a host runtime

For plugins loaded into a host process you don't control (AssettoServer, game servers, extensible
daemons via `AssemblyLoadContext`). The failure class is unique: code that compiles and passes unit
tests, then crashes only inside the real host — so the hunt targets the **published artifact** and
the **host's instantiation path**, not just your logic.

## Scenarios

- **Forbidden-construct inspection (Mono.Cecil on the PUBLISHED DLL)**: maintain the list of
  constructs the host runtime cannot handle and assert their absence by reading the shipped
  assembly, not the sources:

  ```csharp
  using var assembly = AssemblyDefinition.ReadAssembly(publishedDllPath);
  var calls = assembly.MainModule.GetMemberReferences()
      .Where(m => m.DeclaringType.FullName == "Qmmands.CommandContext")
      .Select(m => m.FullName);
  Assert.DoesNotContain("System.IServiceProvider Qmmands.CommandContext::get_Services()", calls);
  ```

  Known examples from a production AssettoServer plugin: `CommandContext.get_Services()` (crashes
  at command time), non-parameterless command-module constructors (host instantiates by
  reflection, DI never runs), `System.Threading.Lock` type references (missing in the host
  runtime — checked via `GetTypeReferences()`). Every new runtime crash earns a new Cecil assert.
- **Publish-shape check**: the artifact triple exists next to the DLL (`.deps.json`,
  `.runtimeconfig.json`); no host assemblies were copied into the plugin output.
- **Host-instantiation test**: drive the plugin through the host's real reflection path (e.g. a
  real `Qmmands.CommandService` + `AddModules(assembly)` + `ExecuteAsync(...)` against a fake
  context) — proving constructors, attributes and reply plumbing survive outside DI.
- **Version-contract check**: the plugin was compiled against the upstream source tag matching the
  runtime release that will load it (build fails hard when the checkout is missing/wrong).

## Rite proof

On a green run, write a machine-readable proof next to the artifact —
`plugin-rite-status.json` with `status`, `checked_at_utc`, `git_commit` — and make the deploy-side
sync script refuse any DLL whose proof is missing **or older than the DLL**. The gate turns "did
you run the bug-hunter?" from a question into a file check.

## Exit criteria

Every known runtime incompatibility has a Cecil assert against the published assembly; the
host-instantiation test passes; the rite proof is written; the deploy gate consumes it. A new
"works in tests, dies in the host" incident is closed only when its construct joins the forbidden
list.
