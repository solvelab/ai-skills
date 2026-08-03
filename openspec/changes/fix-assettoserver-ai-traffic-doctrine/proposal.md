# Change: Fix the AI-traffic baseline in assettoserver-ops — it prescribes a player-blocking bug

## Why

`skills/assettoserver-ops/SKILL.md` publishes a "Validated baseline" YAML block for AI traffic that
is copied verbatim from a production deployment. Two of its values are defects, verified against
AssettoServer source at the pinned runtime tag `v0.0.55-pre25` (2026-08-03):

1. **`MaxPlayerCount: 2` blocks player entry.** It is not a traffic knob.
   `Server/OpenSlotFilters/AiSlotFilter.cs:16-25` returns `false` for **every** car — human slots
   included — once `ConnectedCars.Count` reaches it, and the joining client gets
   `NoSlotsAvailableResponse`. Adopters following this baseline publish a server that advertises
   `MAX_CLIENTS` slots and refuses the third person. Admins bypass the filter, so the operator never
   reproduces it. This shipped to a real server and was found only when a third pilot could not join.

2. **`MaxAiTargetCount: 18` against 25 `AI=Fixed` slots silently kills 7 slots.**
   `Server/Ai/AiBehavior.cs:466` computes `overbooking = targetAiCount / aiSlots.Count` with
   **integer division**: `18 / 25 = 0`, `rest = 18`. Slots at index `>= rest` get
   `SetAiOverbooking(0)` and never spawn. In the deployment this baseline came from, that meant 7 of
   25 traffic models never appeared in-game while clients still downloaded and checksummed all 25 —
   and the models that did spawn skewed heavily to trucks and buses.

The root authoring failure is the same for both: the skill prescribes **magic numbers with no model
behind them**, so neither an adopter nor a reviewer can tell a good value from a harmful one. The
skill also states the rule "keep `MaxAiTargetCount` <= the number of `AI=Fixed` slots", which is
exactly backwards — that inequality is what produces dead slots.

## What Changes

- Rewrite `## AI traffic — enablement discipline` in `skills/assettoserver-ops/SKILL.md`:
  - publish the actual AI-count formula from `AiBehavior.AdjustOverbooking` so every prescribed
    number is checkable;
  - state that `MaxAiTargetCount` is a **total budget summed across all players**, not a CPU ceiling,
    and that upstream's own auto-value (both keys `0`) is `humanSlots * aiSlots`;
  - flag `MaxPlayerCount` as an **entry limit** with a "keep it 0" rule and the two amplifiers that
    hide it (admin bypass, loading-screen players counted for up to
    `PlayerLoadingTimeoutMinutes`);
  - replace the "<= slot count" rule with the correct one: below the slot count, slots die;
  - record that a player never sees more AI cars than the AI-slot count, because
    `EntryCar.cs:241` (`GetBestStateForPlayer`) emits one update per slot per player;
  - record that `Min/MaxAiSafetyDistanceMeters` are **spawn-placement gates**, not following
    distance (`AiState.cs:188` `_minObstacleDistance` governs following), and that the draw is
    uniform in **squared** metres, so the Min barely moves the mean.
- Add the derived-runtime-state gotcha to the orchestration section: the server writes its compiled
  AI spline cache to `cache/` **relative to the process working directory** and creates it at
  runtime, so it must be linked to a mounted path or it is rebuilt on every container start.
- Name the metrics that answer "is the AI count too high", replacing the current
  reduce-`MaxAiTargetCount`-and-hope advice.
- Bump `metadata.version` 1.2.0 -> 1.3.0 and regenerate all tool wrappers via `./generate.sh`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — a skill that prescribes numeric configuration SHALL
  publish the rule that produces the numbers, and SHALL NOT present a snapshot copied from a
  deployment as a validated baseline without deriving it.

## Impact

- `skills/assettoserver-ops/SKILL.md` (AI traffic section, orchestration section, version) plus the
  regenerated `claude/`, `codex/`, `cursor/`, `copilot/` and `plugins/devops/` wrappers.
- No category change, no new skill, no README table change (description and triggers unchanged).
- Adopters of the current baseline inherit both defects; the corrected section states them
  explicitly so an existing deployment can be audited rather than silently re-copied.
