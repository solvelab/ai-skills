# Design: corrected AI-traffic doctrine for assettoserver-ops

## Approach

The current section fails because it teaches *values*. The fix is to teach the *rule*, then let the
values follow — a reader who has the formula can audit their own server, which no amount of
corrected constants achieves.

The formula is small enough to publish verbatim (`Server/Ai/AiBehavior.cs:453-476`):

```csharp
int playerCount = EntryCars.Count(car => car.Client != null && car.Client.IsConnected);
var aiSlots     = EntryCars.Where(car => car.Client == null && car.AiControlled).ToList();
int targetAiCount = Math.Min(
        playerCount * Math.Min((int)Math.Round(AiPerPlayerTargetCount * TrafficDensity), aiSlots.Count),
        MaxAiTargetCount);
int overbooking = targetAiCount / aiSlots.Count;   // integer division
int rest        = targetAiCount % aiSlots.Count;
```

Three consequences carry the whole section, so they are stated as rules rather than prose:

| Rule | Why it holds |
|---|---|
| `MaxAiTargetCount` >= number of `AI=Fixed` slots, or slots die | `overbooking = target / slots` is integer division; slots at index `>= rest` get 0 states |
| `MaxAiTargetCount` is a budget across **all** players, so size it `perPlayer * maxPlayers` | the outer `Math.Min` caps the sum, not the per-player share |
| A player never sees more than `aiSlots.Count` AI cars | `EntryCar.cs:241` emits one `PositionUpdateOut` per slot per player via `GetBestStateForPlayer` |

The safest prescription is therefore **not** a constants block at all: leaving `MaxAiTargetCount`
and `AiPerPlayerTargetCount` at `0` makes AssettoServer compute `aiSlots` and `humanSlots * aiSlots`
itself (`Server/Configuration/ACServerConfiguration.cs:281-289`) — which is correct by construction
for any entry list. The skill keeps a worked example, but frames it as *derived*, with the auto
default as the recommended starting point.

`MaxPlayerCount` moves out of the traffic block entirely: it is an entry limit that happens to live
under `AiParams`, and grouping it with density knobs is what made the bug invisible.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| AI-traffic sizing math, slot/overbooking rules, entry-limit trap | `assettoserver-ops` | establish here (canonical) |
| Runtime dirs that must be linked to mounted paths (incl. the spline cache) | `assettoserver-ops` | already canonical — extend the existing orchestration section |
| Plugin-side loops over `EntryCarManager.EntryCars` that scale with AI count | `assettoserver-plugin` | link only; do not restate plugin internals here |
| Client-side car-count scans in CSP overlays | `assettoserver-csp-lua` | out of scope, untouched |
| Adversarial verification of a just-changed config | `bug-hunter` | link (already canonical, unchanged) |

## Risks / Trade-offs

- [Section grows and buries the enablement gate] → the prerequisite gate (lane file, `AI=Fixed`,
  `MAX_CLIENTS` recount) stays first and numbered; the math follows as a separate subsection.
- [Publishing a formula ages badly if upstream changes it] → the formula is cited with file:line and
  the pinned tag `v0.0.55-pre25`, so a reader can diff it against their own runtime.
- [Removing the constants block loses a working starting point] → keep a worked example, but derived
  from the formula and labelled as such, with `0`/auto as the recommendation.
- [Stale wrappers if `generate.sh` is skipped] → CI "Wrappers in sync" step fails the PR; the task
  group covers regeneration explicitly.
