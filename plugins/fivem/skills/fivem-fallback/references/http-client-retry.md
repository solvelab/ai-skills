# Reference — resilient HTTP client for FiveM server Lua (production-extracted)

Battle-tested wrapper for every Lua→backend call (extracted from a ~65-resource production server;
names generalized). Design points, each earned by a real incident:

- **Retry ONLY on 5xx, bounded (10×)** — a 4xx is an *answer* (validation, auth, not-found), not a
  transport failure; retrying it just repeats the rejection. Same doctrine as the negative-cache
  rule in the skill: only the path that indicates a *server/transport* fault retries.
- **Blocking via promise + `Citizen.Await`** — callers get a plain return value; no callback
  pyramids in 30+ consumer modules.
- **Service-token header injected without overwriting** — if the caller set the header explicitly,
  respect it; otherwise inject from a convar. (`os.getenv` returns nil in fxserver Lua — convars
  set by the entrypoint are the only channel for env config.)
- **Loud-fail placeholder host** — defaulting the hostname to `__BACKEND_HOSTNAME_UNSET__` makes a
  misconfigured boot fail with an obvious bad-host error instead of silently calling localhost.
- **`filterError`** — normalizes error payloads (anything carrying `statusCode`) to `{}` so
  consumers can do shape-checks without spreading nil-guards.

```lua
-- HttpRequest.lua — shared HTTP wrapper (server-side only).
HttpRequest = {}

-- Convars are set by the container entrypoint from env vars.
HttpRequest.api_path = GetConvar("backend_hostname", "__BACKEND_HOSTNAME_UNSET__")
HttpRequest.api_prefix = GetConvar("backend_api_prefix", "/api/v1")

-- Service-auth token (shared secret with the backend). Empty = not configured
-- (backend in rollout mode permits without it). Sent on EVERY call so the API
-- can verify the caller is the authorized game server, not a forged client.
HttpRequest.service_token = GetConvar("backend_service_token", "")

function HttpRequest:call(source, headers, path, method, payload)
  headers = headers or {}
  -- Inject the service token (if configured) without overwriting a caller-set header.
  if HttpRequest.service_token ~= "" and headers["X-Service-Token"] == nil then
    headers["X-Service-Token"] = HttpRequest.service_token
  end

  local repeatRequest, countRequest, resultRequest = 10, 0, nil
  local fullPath = HttpRequest.api_path .. HttpRequest.api_prefix .. path

  while countRequest < repeatRequest do
    countRequest = countRequest + 1
    local prom = promise.new()
    PerformHttpRequest(fullPath, function(resultCode, resultData, resultHeaders)
      prom:resolve({
        resultCode = resultCode,
        resultData = json.decode(resultData),
        resultHeaders = resultHeaders,
      })
    end, method, json.encode(payload), headers)
    local result = Citizen.Await(prom)

    resultRequest = HttpRequest:validateResponse(source, result, payload, fullPath, method, countRequest)
    -- 4xx/2xx = an ANSWER → stop. Only 5xx (server fault) retries.
    if resultRequest == nil or resultRequest.resultCode == nil or resultRequest.resultCode < 500 then
      break
    end
  end
  return resultRequest
end

function HttpRequest:validateResponse(sessionId, result, payload, path, method, countRequest)
  local log = ("StatusCode: %s | path: %s | method: %s | attempt %d"):format(
    tostring(result.resultCode), tostring(path), tostring(method), countRequest)
  if result.resultCode >= 500 then
    print("[http-client][ERROR] " .. log)
    return result                       -- keep the wrapper shape → loop retries
  end
  if countRequest > 1 then
    print("[http-client][WARN] recovered after retry — " .. log)
  end
  return result.resultData              -- decoded body → loop breaks
end

function HttpRequest:post(source, path, options)
  options = options or {}
  return HttpRequest:call(source, options.headers or {}, path, "POST", options.payload or {})
end

function HttpRequest:get(source, path, options)
  options = options or {}
  return HttpRequest:call(source, options.headers or {}, path, "GET", options.payload or {})
end

-- Normalize error payloads: anything carrying statusCode becomes {} (logged),
-- so consumers can shape-check (`type(res.data) == "table"`) without nil-guards.
function HttpRequest:filterError(payload, event)
  if payload == nil then return {} end
  if payload.statusCode then
    print("[http-client][ERROR] payload error: " .. json.encode(payload) .. " | " .. tostring(event))
    return {}
  end
  return payload
end

function GetHttpRequestInstance()
  return HttpRequest
end
```

Consumption pattern: one **bridge resource** owns all backend calls (per-domain modules, each
registering named exports); every other resource calls `exports["rest-bridge"]:DomainAction(...)`
and never touches HTTP directly. Identity (`session_id`, `acting_session_id`) is always explicit in
the payload — the wrapper never auto-injects it (a server-op with no player must not inherit one).
