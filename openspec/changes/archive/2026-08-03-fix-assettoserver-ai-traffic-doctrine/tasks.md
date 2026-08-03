## 1. AI traffic section

- [x] 1.1 Published the `AdjustOverbooking` formula (`Server/Ai/AiBehavior.cs:453-476`, tag
      `v0.0.55-pre25`) so every prescribed number is checkable
- [x] 1.2 Replaced the rule "keep `MaxAiTargetCount` <= the number of `AI=Fixed` slots" with the
      correct one — below the slot count, integer division zeroes the tail slots and those models
      never spawn
- [x] 1.3 Stated that `MaxAiTargetCount` is a total budget across all players (size it
      `perPlayer * maxPlayers`), and recommended the upstream auto value (both keys `0` ->
      `aiSlots` and `humanSlots * aiSlots`, `ACServerConfiguration.cs:281-289`)
- [x] 1.4 `MaxPlayerCount` moved out of the traffic block into its own subsection: ENTRY limit that
      closes every slot (`AiSlotFilter.cs:16-25`), rule to keep it `0`, plus the admin-bypass and
      loading-screen amplifiers
- [x] 1.5 Recorded the per-player ceiling: one `PositionUpdateOut` per slot per player via
      `GetBestStateForPlayer` (`EntryCar.cs:241`)
- [x] 1.6 Recorded that `Min/MaxAiSafetyDistanceMeters` are spawn-placement gates, not following
      distance (`AiState.cs:188` `_minObstacleDistance`), and that the draw is uniform in squared
      metres, so the Min barely moves the mean
- [x] 1.7 Example block reframed: `MaxPlayerCount: 0`, both target keys `0` (server-derived) with
      inline comments; no longer labelled "validated baseline"

## 2. Orchestration section

- [x] 2.1 Added the derived-runtime-state rule: the AI spline cache is written to `cache/`
      relative to the working directory and created at runtime, so it never shows up in a
      hand-written mount list; unlinked it is recompiled on every container start
- [x] 2.2 Noted the follow-ons: freshly provisioned volume is root-owned and needs a `chown` before
      first boot; the cache is derived data (single-replica storage, out of backups, safe to
      delete). Also noted that a named volume over the install dir hides this locally

## 3. Observability

- [x] 3.1 Replaced "if CPU/FPS get heavy, lower `MaxAiTargetCount`" with the four metrics and the
      single-thread tick budget they are read against, plus the note that bandwidth usually binds
      before CPU

## 4. Catalog mechanics

- [x] 4.1 Bumped `metadata.version` 1.2.0 -> 1.3.0
- [x] 4.2 `./generate.sh` run; wrappers regenerated. Verified the split: `claude/`, `codex/` and
      `copilot/` are pointer wrappers (only the version line moves), `cursor/` and
      `plugins/devops/` embed the content and both carry the new sections

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform: name == directory, folded description, author solvelab, version
      1.3.0 semver, category `devops` in the controlled set, license MIT, compatibility present
- [x] Q.2 All touched content in English
- [x] Q.3 Description unchanged, so triggers and the "Do NOT use for" boundary vs
      `assettoserver-plugin` / `python-rest-api` are intact; README table row needs no edit and the
      skill count stays 30
- [x] Q.4 No duplicated doctrine: plugin-side per-tick loops explicitly deferred to
      `assettoserver-plugin`; client-side car scans untouched in `assettoserver-csp-lua`.
      `references/` re-grepped — they carried none of the corrected values, so no edit needed
- [x] Q.5 Adversarial re-read against the pinned tag. Four claims that came from analysis rather
      than first-hand reading were re-verified in source before publishing:
      `Metrics.CreateSummary("assettoserver_acserver_updateasync")` and
      `CreateCounter("...updateasync_late")` (`ACServer.cs:192,194`),
      `CreateGauge("assettoserver_aistatecount")` + `CreateSummary("assettoserver_aibehavior_update")`
      (`AiBehavior.cs:33,60`), `new EntryCar[Math.Min(MaxClients, EntryList.Cars.Count)]`
      (`EntryCarManager.cs:242`), `PlayerLoadingTimeoutMinutes = 10`
      (`ACExtraConfiguration.cs:77`), and `CLIENT_SEND_INTERVAL_HZ` -> `RefreshRateHz = 20`
      (`ServerConfiguration.cs:19`). All present and matching.

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate fix-assettoserver-ai-traffic-doctrine --strict` green
- [x] V.2 `scripts/validate-rite.sh` green — 3 passed, 0 failed, "rite gate OK"
- [x] V.3 Wrappers in sync: second `./generate.sh` produced an empty `git diff` (idempotent)
- [x] V.4 Catalog discovery intact: 30 skills generated, `devops` plugin group unchanged, README
      table and counts untouched
- [x] V.5 `openspec archive fix-assettoserver-ai-traffic-doctrine --yes` — done on the branch,
      matching the repo precedent (#20); `openspec validate --specs --strict` green afterwards
