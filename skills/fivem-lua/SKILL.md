---
name: fivem-lua
description: >-
  Conventions for writing FiveM (CitizenFX) server/client Lua resources. Use when working on FiveM/FXServer Lua — RegisterNetEvent/RegisterNUICallback handlers, fxmanifest, exports, NUI (SendNUIMessage/SetNuiFocus), threads/CreateThread, StateBags, or natives. Enforces the client-is-never-trusted boundary (validate payload + derive actor from `source`), explicit fxmanifest order, no busy `while true` loops, module-per-global pattern, and NUI focus/disconnect cleanup. Do NOT use for react-three-fiber or non-FiveM Lua.
metadata:
  author: solvelab
  version: 1.2.0
  category: fivem
license: MIT
compatibility: Works in any environment with filesystem access.
---

# FiveM Lua — CitizenFX conventions

Generic conventions for writing maintainable server/client Lua resources on FiveM (CitizenFX).
Project-agnostic: resource prefixes, exact endpoints, and keybind registries belong in the project's
own CLAUDE.md, not here.

## Trust boundary (the most important rule)

- **The client is never trusted.** Any value a client sends to the server (event args, NUI callback
  payload) is attacker-controlled. Validate type, presence, and range on the server before use.
- **Derive the actor from `source`**, never from a client-supplied id. In a server `RegisterNetEvent`
  handler, `source` is the real sender. If the handler acts on *another* player (`targetServerId`),
  check the relationship/permission and rate-limit it — otherwise it's an injection/DoS vector.
- Server is authoritative for state and money/assets. The client only *requests*.
- **Anti-forge merge** for telemetry the server can also read: treat the client report as a
  *clamped hint* and let the server-side read of the live entity WIN when available:

```lua
local snap = {
  body = clampNum(clientCond.body, 0.0, 1000.0),   -- client hint, clamped
  fuel = clampNum(clientCond.fuel, 0.0, 100.0),
}
local live = exports["vehicle-owner-res"]:GetLiveCondition(src)
if live and live.engine then snap.engine = live.engine end  -- server-read PREVAILS
```

```lua
RegisterNetEvent("res:doThing", function(targetId, amount)
  local src = source                        -- trusted
  targetId = tonumber(targetId)
  amount = tonumber(amount)
  if not targetId or not amount then return end          -- presence/type
  if amount <= 0 or amount > MAX then return end          -- range
  if targetId == src then return end                      -- sanity
  -- + permission/relationship check before acting on targetId
end)
```

## fxmanifest

- Use **explicit file order** in `client_scripts`/`server_scripts`/`shared_scripts`. Avoid glob
  `**/*.lua` — load order is undefined and breaks module-extends-global patterns. A glob is
  acceptable ONLY when the files are provably order-independent (e.g. a bridge whose modules never
  reference each other) — and then the exception must be documented in the resource README.
- Declare `fx_version`, `game 'gta5'`, and `lua54 'yes'`.
- Declare `exports`/`server_exports` for the public cross-resource API.
- **Unique basenames** for every Lua file in a resource — never repeat a file name across
  subfolders (e.g. `actions/foo/def.lua` + `actions/bar/def.lua`). Lua error traces show only the
  basename+line (`def.lua:15` is ambiguous across N folders), globs/tooling and humans confuse the
  copies, and same-named files have caused real malfunctions in practice. Prefix with the parent
  folder/domain instead: `actions/foo/foo_def.lua`, `actions/bar/bar_behavior.lua`.

## Threads — no busy loops

- **Never `while true do ... Wait(0) end`** as an always-on loop. It burns CPU even when idle.
- Run threads **on-demand**, gated by a state flag; exit the loop when the flag clears. Use
  `SetTimeout` for one-shots and event-driven triggers instead of polling.

```lua
local active = false
local function startLoop()
  if active then return end
  active = true
  CreateThread(function()
    while active do
      -- work
      Wait(200)                 -- never Wait(0) unless truly per-frame is required
    end
  end)
end
local function stopLoop() active = false end
```

## Module pattern

- **One global table per resource**; modules extend it (`Helpers.lua` defines `X`; others add `X.Sub = {}`).
- Keep files small (~≤300 lines); split by domain into `events/`, `modules/<Domain>.lua`.
- Cross-resource API goes through `exports`, not globals.

## Cross-resource events & new-resource checklist

- **Never hardcode cross-resource event names** — keep one shared catalog resource exposing
  constants (`GetEventsInstance()`), so a typo is a nil-index error at the call site instead of a
  handler that silently never fires. Full pattern (catalog, decision tree, declared boot order,
  optional per-session encryption): `references/events-registry.md`.
- Wiring a NEW resource takes four points, all of them — a miss means "silently never started":
  1. entry in the shared **event catalog** (if it has cross-resource events);
  2. entry in the **declared boot order** (the layer list the spawn orchestrator iterates);
  3. `ensure <name>` in the server cfg;
  4. the dev **ensure-script/list** used after isolated restarts.

## Natives

- Confirm the native exists for `gta5` and check its signature (arg types + order) in the official
  docs before using it. Don't invent names from other games.
- Wrap fallible natives / external calls in `pcall` so one failure doesn't kill the thread.

## NUI

- NUI build artifacts live in the conventional `client/html/` location for the project.
- `SendNUIMessage` (Lua→JS) and `RegisterNUICallback` (JS→Lua). **Validate the callback payload** —
  it can be forged from the browser/devtools.
- **Always pair `SetNuiFocus(true, true)` with `SetNuiFocus(false, false)`** on every close path
  (button, ESC, error, disconnect). A missed unfocus locks the cursor and blocks gameplay.

## State & lifecycle

- Synced networked state via StateBags is convenient but **not concurrency-safe** — concurrent writers
  can race. Treat the server as the serialization point for anything that must be consistent.
- **Clean up on disconnect/resource-stop**: release locks, clear per-player tables, stop threads.
  `playerDropped` / `onResourceStop` handlers must undo what the resource set up. Orphaned state after
  a player leaves is a common bug source.
- **Hot-reload gotcha**: a NEW Lua file never loads via resource restart — the manifest cache only
  re-reads files it already knew. New files ⇒ full server restart. And when the fxmanifest itself
  changed, wipe the resource's server cache (stale `.rpf` ⇒ scripts silently nil).

## See also

- `fivem-fallback` — resilience when calling an external backend from Lua.
- `bug-hunter` — adversarial testing; its `references/track-fivem-lua.md` exercises the trust-boundary
  and lifecycle rules defined here.
- `backend-resilience` — the stack-agnostic doctrine behind `fivem-fallback`.
- `fivem-nui-react` — the React/CEF side of NUI (bridge hooks, uiReady handshake, rendering quirks).
