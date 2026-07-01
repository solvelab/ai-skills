---
name: backend-resilience
description: >-
  Resilience and fallback patterns for any service calling an unreliable dependency — external API,
  config store (Consul/KV), database, message broker, or another internal service. Use when adding or
  reviewing code that makes network calls that can time out, return 5xx, return partial payloads, or
  hit a dependency that is down — or when adding config fetch, retry logic, caching of failures, or
  degraded-mode behavior. Enforces safe defaults, one shared fallback helper, response-shape validation,
  clamping of remote values, bounded retries, negative caching, and in-flight deduplication. Examples in
  Python; the doctrine is language-agnostic. For the FiveM/Lua adaptation use fivem-fallback instead.
metadata:
  author: solvelab
  version: 1.0.0
  category: backend
license: MIT
compatibility: Works in any environment with filesystem access.
---

# Backend resilience & fallback

Defensive patterns for calling an unreliable dependency. The network boundary is unstable: timeouts,
5xx, partial payloads, dependency down, races. Every call needs a **safe default** so the service keeps
working. Doctrine is stack-agnostic; examples are Python.

## Principles

1. **Every external call can fail.** A failed call must produce a safe default — never a crash, and
   never silent stale state presented as fresh.
2. **One shared helper, not ad-hoc per module.** Scattered try/except + type-check copies drift.
   Provide a single `safe_call`/`with_fallback` utility and use it everywhere.
3. **Validate the response shape**, not just transport success: check the type, the expected fields,
   and the status/code before trusting the data.
4. **Clamp untrusted/remote numbers** into a sane range — a bad config value must not break the system.
5. **Bound retries.** If the HTTP client already retries 5xx, don't stack an unbounded second retry
   loop on top. Total attempts across all layers must be finite and known.

## safe_call / clamp

```python
from typing import Callable, TypeVar

T = TypeVar("T")

def safe_call(fn: Callable[[], T], fallback: T) -> tuple[bool, T]:
    """Returns (ok, value). On any failure returns (False, fallback) — never raises."""
    try:
        return True, fn()
    except Exception:
        return False, fallback

def clamp_num(value, lo: float, hi: float, default: float) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, v))
```

## Config / KV with hardcoded fallback

Remote config (Consul KV, a `/config/*` endpoint) WILL be unavailable sometimes. Always ship a
hardcoded default and merge field-by-field; clamp ranges.

```python
FALLBACK = {"xp_per_level": 100, "max_level": 50}   # hardcoded safe default

ok, cfg = safe_call(lambda: kv_client.get_json("game/config"), None)
if not ok or not isinstance(cfg, dict):
    cfg = dict(FALLBACK)                            # degrade, don't crash — and log it
max_level = clamp_num(cfg.get("max_level"), 1, 999, FALLBACK["max_level"])
```

## Negative cache (avoid timeout cascade)

When a dependency is unreachable, cache the *failure* briefly (a few seconds) so every subsequent call
doesn't wait out the full timeout. Re-query after the fail-TTL expires.

**Exception:** a real 404 / "not found" is an answer, not a transport failure — do NOT negative-cache it.

```python
_fail_until = 0.0
FAIL_TTL = 15.0

def get_price(item_id: str) -> float | None:
    global _fail_until
    if time.monotonic() < _fail_until:
        return None                                  # known-down: fail fast
    try:
        return pricing_client.get(item_id)           # a 404 here returns None, not an exception
    except TransportError:
        _fail_until = time.monotonic() + FAIL_TTL    # transport failure: back off
        return None
```

## Startup config: retry then degrade

At boot, retry the config fetch a bounded number of times, then start in degraded mode on the hardcoded
fallback — a config outage must not prevent startup. Log the degradation and refresh when the
dependency recovers (background task, health-check hook, or next request).

## Surface failures to the caller

A handler that depends on a downstream call must tell its caller when that call failed — an explicit
error response or degraded-data marker — never a silent success with stale/empty data. (HTTP: 503 with
a Problem Details body beats a fabricated 200.)

## Concurrency: deduplicate in-flight requests

Guard against duplicate concurrent requests for the same key (single-flight / per-key lock) so N
concurrent triggers don't spawn N identical downstream calls and overwrite each other out of order.

## See also

- `api-resilience-testing` — how to *test* an API against these failure modes (negative/fuzz/contract).
- `bug-hunter` — the adversarial-testing rite that validates fallback under "dependency down / partial
  payload / race".
- `fivem-fallback` — the FiveM/Lua adaptation of this doctrine.
