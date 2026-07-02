---
name: react-api-client
description: >-
  Conventions for React SPAs consuming a typed-envelope REST API (the frontend counterpart of
  python-rest-api), distilled from a production platform frontend. Use when building or reviewing a
  React app that talks to a backend — API client with envelope discipline and typed error codes,
  zod domain parsers that throw on payload drift, auth store factory (tokens-only persistence,
  single-flight refresh, handler injection), realtime as a polling facade, and dedup nonces on paid
  mutations. Not for FiveM NUIs (CEF) — that is fivem-nui-react.
metadata:
  author: solvelab
  version: 1.0.0
  category: frontend
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

# React SPA ↔ typed-envelope API

The backend (`python-rest-api` skill) speaks `{status, code, message, data}`. These conventions
keep the frontend honest about it: the front only EXHIBITS state and SENDS intents — balance,
cost, cooldown, permission and availability are validated server-side, always.

## API client (axios wrapper)

- Thin typed verbs (`get/post/put/patch/delete<T>`) that return `res.data` — the client does NOT
  unwrap the envelope; domain parsers do (see below). Factory (`createApiClient`), never a
  singleton import: each app wires its own baseURL/handlers.
- **Handler injection breaks the api⇄auth import cycle**: `setAuthHandlers({ getAccessToken,
  onUnauthorized, refresh? })` — the client never imports the auth store.
- Error contract, enforced in ONE response interceptor:
  - **401** → single-flight `refresh()` (concurrent 401s share one in-flight promise) → retry the
    original request exactly once (`_retried` guard) → still failing ⇒ `onUnauthorized()` +
    `UNAUTHORIZED`. If the app has no refresh endpoint, omit `refresh` — a 401 logs out
    immediately (explicit, not accidental).
  - **403** → `NOT_PERMITTED`, and it NEVER logs the user out.
  - Everything else → `normalizeError` → typed `ApiException`.
- `skipAuth` per-request flag for login/refresh routes (no Authorization injection, no retry loop).

Implementation: `references/api-client.md`.

## Typed error taxonomy

- One `ErrorCodes` enum for every code the UI branches on (`INSUFFICIENT_BALANCE`,
  `COOLDOWN_ACTIVE`, `TARGET_OFFLINE`, `LIMIT_REACHED`, `NOT_PERMITTED`, `UNAUTHORIZED`,
  `NETWORK`, `UNKNOWN`, ...). `normalizeError` maps: no response → `NETWORK` (timeout vs offline
  message); known body `code` → itself; else status-derived; else `UNKNOWN`.
- **Callers branch on `err.code` only** — never on HTTP status, never on message strings. Raw
  backend codes outside the enum stay readable on `err.raw.code` for feature-specific handling.

## Domain parsers: throw on drift

Every response body goes through a zod schema per domain that validates the envelope AND
transforms snake_case → camelCase. A missing/wrong-typed field **throws** — a forged or partial
payload is a failure, never a half-built cache entry. The parser is the only place that knows the
wire shape.

## Auth store (factory, not singleton)

- `createAuthStore({ persistKey })` — zustand vanilla store per app.
- **Persist ONLY tokens** (`partialize`); `user`/`isAuthenticated` are re-derived at boot via
  `GET /auth/me` — never trusted from storage.
- Probe localStorage with a real write and degrade to an in-memory Map (private-mode safe).
- Boot gate: token-but-no-user → fetch `/me` → `setSession`, else `clear()`; guard StrictMode
  double-mount with a `cancelled` flag.

## Realtime = facade over polling

- Define a `RealtimeAdapter` interface consumed via one hook (`useRealtimeChannel`); ship a
  `PollingAdapter` with per-domain cadence (wallet 10s, presence 15s, ranking 30s...), ref-counted
  subscriptions, and `apply()` distinguishing **delta** (`setQueryData`) from **signal**
  (`invalidateQueries`). SSE/WS arrive later as adapters — zero consumer churn.

## Paid mutations: dedup nonce

Every mutation that charges money carries a client-generated `dedup_key`
(`crypto.randomUUID()` with a time+random fallback for non-secure contexts — LAN/IP access has no
`crypto.randomUUID`). The backend makes the retry a no-op; the double-click double-charge class of
bug dies at the contract level.

## See also

- `python-rest-api` — the backend envelope/code registry these conventions consume.
- `fivem-nui-react` — React inside the game's CEF (different transport, same discipline).
