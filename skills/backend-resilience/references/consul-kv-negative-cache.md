# Reference — Consul KV client with negative cache (Python)

Battle-tested reference implementation (extracted from a production game backend). The motivating
incident: with the Consul host down, every request paid the **full HTTP timeout** (+2s on every
endpoint that read config). With the negative cache it costs **one attempt per key per fail-TTL**,
never per request.

Design points:

- **Two caches**: positive (30s) for parsed values, negative (15s) for the *fallback* — checked in
  that order before any HTTP call.
- **Only transport errors negative-cache** (`httpx.HTTPError`, `OSError`) — that's the only path that
  pays the timeout. A 404, a non-200, or invalid JSON are *fast* answers from a live Consul (~ms) and
  the key may be created/fixed at any moment — caching them would delay the override with no latency
  win.
- **Never raises.** Read returns the fallback; write returns `bool` and the caller decides.
- **ACL auto-detection**: try without a token first; on 401/403 retry with `X-Consul-Token`. One code
  path serves both ACL-off and ACL-on clusters.
- `invalidate_cache()` is exposed for tests (reset module state between tests — autouse fixture) and
  after writes.

```python
"""Minimal Consul KV client — HTTP /v1/kv with in-memory cache + fallback."""
from __future__ import annotations

import base64
import json
import time
from typing import Any, Optional

import httpx
import structlog

from app.core.config import Settings   # CONSUL_HOST/PORT/PREFIX/TIMEOUT_S/TOKEN/WRITE_TOKEN

logger = structlog.get_logger(__name__)

_CACHE_TTL_SECONDS = 30.0
# NEGATIVE cache — ONLY for TRANSPORT errors (timeout / unreachable host).
# 404 / HTTP!=200 / invalid JSON do NOT cache: they are FAST answers from a live
# Consul and the key can be created/fixed at any moment.
_FAIL_TTL_SECONDS = 15.0
_cache: dict[str, tuple[float, Any]] = {}
_fail_cache: dict[str, tuple[float, Any]] = {}


def _consul_url(settings: Settings, key: str) -> str:
    return f"http://{settings.CONSUL_HOST}:{settings.CONSUL_PORT}/v1/kv/{key}"


def _full_key(settings: Settings, relative: str) -> str:
    return f"{settings.CONSUL_PREFIX.rstrip('/')}/{relative.lstrip('/')}"


def _send_with_acl(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    content: Optional[str] = None,
    token: Optional[str] = None,
) -> httpx.Response:
    """Try WITHOUT a token first; if Consul answers 401/403 (ACL required) and a
    token exists, retry WITH `X-Consul-Token`. Serves ACL-off and ACL-on clusters."""

    def _do(headers: dict) -> httpx.Response:
        if method == "GET":
            return client.get(url, headers=headers)
        return client.put(url, content=content, headers=headers)

    resp = _do({})
    if resp.status_code in (401, 403) and token:
        resp = _do({"X-Consul-Token": token})
    return resp


def get_json(relative_key: str, fallback: Optional[Any] = None) -> Any:
    """Read a JSON value from Consul KV. Returns fallback on ANY failure."""
    settings = Settings()
    full_key = _full_key(settings, relative_key)

    cached = _cache.get(full_key)
    if cached and (time.monotonic() - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]
    failed = _fail_cache.get(full_key)
    if failed and (time.monotonic() - failed[0]) < _FAIL_TTL_SECONDS:
        return failed[1]                      # cached fallback — no new HTTP attempt

    try:
        url = _consul_url(settings, full_key)
        with httpx.Client(timeout=settings.CONSUL_TIMEOUT_S) as client:
            resp = _send_with_acl(client, "GET", url, token=settings.CONSUL_TOKEN)
        if resp.status_code == 404:
            logger.warning("consul_key_missing", key=full_key)
            return fallback
        if resp.status_code != 200:
            logger.warning("consul_http_error", key=full_key, status=resp.status_code)
            return fallback
        rows = resp.json()
        if not rows:
            return fallback
        raw_value = rows[0].get("Value")
        if raw_value is None:
            return fallback
        decoded = base64.b64decode(raw_value).decode("utf-8")
        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError:
            logger.warning("consul_json_decode_failed", key=full_key)
            return fallback
        _cache[full_key] = (time.monotonic(), parsed)
        _fail_cache.pop(full_key, None)
        return parsed
    except (httpx.HTTPError, OSError) as exc:
        # ONLY here we negative-cache: this is the path that pays the full timeout.
        logger.warning("consul_unreachable", key=full_key, err=str(exc))
        _fail_cache[full_key] = (time.monotonic(), fallback)
        return fallback


def put_json(relative_key: str, value: Any) -> bool:
    """Write `value` (JSON) to Consul KV. 200 → invalidate read cache + True.
    Any error → log + False (NEVER raises: the caller decides what False means)."""
    settings = Settings()
    full_key = _full_key(settings, relative_key)
    try:
        url = _consul_url(settings, full_key)
        body = json.dumps(value, ensure_ascii=False, indent=2)   # human-readable KV
        with httpx.Client(timeout=settings.CONSUL_TIMEOUT_S) as client:
            resp = _send_with_acl(client, "PUT", url, content=body,
                                  token=settings.CONSUL_WRITE_TOKEN)
        if resp.status_code != 200:
            logger.warning("consul_put_http_error", key=full_key, status=resp.status_code)
            return False
        invalidate_cache()
        return True
    except (httpx.HTTPError, OSError) as exc:
        logger.warning("consul_put_unreachable", key=full_key, err=str(exc))
        return False


def invalidate_cache() -> None:
    _cache.clear()
    _fail_cache.clear()
```

Testing notes: patch `httpx.Client` (the helper uses `client.get`/`client.put`, not `.request`, so
mocks stay simple) and reset module state between tests with an autouse fixture calling
`invalidate_cache()`.
