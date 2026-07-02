---
name: fivem-fallback
description: >-
  FiveM/Lua adaptation of the backend-resilience doctrine: safe defaults, SafeCall/clampNum helpers,
  boot-time config retry, negative cache and NUI error signaling for FiveM resources calling an external
  backend, config store (Consul/KV), or another resource. Use when a FiveM resource makes HTTP/export
  calls that can time out, return 5xx, return partial payloads, or hit a dependency that is down — or
  when adding config fetch, NUI callbacks that call the backend, or retry logic in Lua. For non-FiveM
  services use backend-resilience instead.
metadata:
  author: solvelab
  version: 1.2.0
  category: fivem
license: MIT
compatibility: Works in any environment with filesystem access.
---

# FiveM fallback & resilience (Lua adaptation)

**Doctrine lives in `backend-resilience`** — read it first: safe defaults, one shared helper,
response-shape validation, clamping, bounded retries, negative cache (never negative-cache a real 404),
in-flight dedupe. This skill is the FiveM/Lua mechanics only.

## SafeCall / clampNum (Lua)

```lua
-- Returns (ok, value). On any failure returns (false, fallback) — never throws.
local function SafeCall(fn, fallback)
  local ok, res = pcall(fn)
  if not ok then return false, fallback end
  return true, res
end

local function clampNum(v, lo, hi, default)
  v = tonumber(v)
  if not v then return default end
  if v < lo then return lo elseif v > hi then return hi end
  return v
end
```

## Config via exports with hardcoded fallback

```lua
local FB = { xpPerLevel = 100, maxLevel = 50 }     -- hardcoded safe default
local ok, cfg = SafeCall(function() return exports["rest-api"]:ConfigJob() end, nil)
if not ok or type(cfg) ~= "table" or type(cfg.data) ~= "table" then
  cfg = { data = FB }                               -- degrade, don't crash
end
local maxLevel = clampNum(cfg.data.maxLevel, 1, 999, FB.maxLevel)
```

Validate the shape (`type(cfg) == "table"`, expected field present, expected status/code) before
trusting `data` — transport success is not payload validity.

## Boot-time config: retry then degrade (CreateThread)

```lua
CreateThread(function()
  for _ = 1, 20 do
    local ok = SafeCall(refreshConfig, false)
    if ok then return end
    Wait(3000)
  end
  -- still down → run on hardcoded fallback; log it; let a later event refresh
end)
```

## NUI callbacks must signal failure

A NUI callback that triggers a backend call must tell the UI when it fails — otherwise the panel shows
stale state with no error. Don't leave the callback hanging; send an explicit error back.

```lua
RegisterNUICallback("buy", function(data, cb)
  local ok, res = SafeCall(function() return exports["rest-api"]:Buy(source, data) end, nil)
  if not ok or type(res) ~= "table" or res.code ~= "OK" then
    cb({ ok = false, error = "unavailable" })       -- UI can show a retry, not freeze
    return
  end
  cb({ ok = true, data = res.data })
end)
```

## Shared HTTP client (retry only on 5xx)

All Lua→backend traffic goes through ONE shared wrapper: bounded retry (10×) **only on 5xx** — a
4xx is an answer, not a transport failure (same doctrine as the 404 negative-cache exception) —
service-token header injected without overwriting the caller's, and a loud-fail placeholder
hostname so misconfig breaks visibly instead of silently hitting localhost. Production-extracted
implementation: `references/http-client-retry.md`.

## Concurrency

Guard against duplicate in-flight requests for the same key (a one-shot flag / dedupe) so concurrent
triggers don't spawn N identical backend calls and overwrite each other out of order — the Lua
equivalent of single-flight.

## See also

- `backend-resilience` — the stack-agnostic doctrine this skill adapts.
- `fivem-lua` — general CitizenFX conventions.
- `bug-hunter` — the Lua track validates fallback under "backend down / partial payload / race".
