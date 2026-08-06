# Change: Add the observability skill

## Why

Executes solvelab/ai-skills#49. The backend family prescribed behaviour that only works if someone can
see it, and no skill said where the seeing happens. Measured across the four skills before this change:

| skill | request-id / correlation | OpenTelemetry | metrics | RED / latency |
|---|---|---|---|---|
| `python-rest-api` | 0 | 0 | 1 | 0 |
| `backend-resilience` | 0 | 0 | 3 | 0 |
| `log-event-collector` | 0 | 0 | 1 (its own lag) | 0 |
| `api-resilience-testing` | 0 | 0 | 0 | 0 |

`backend-resilience` told the shared helper to increment `FALLBACK_TOTAL` and to alert on
`rate(fallback_used)` — while **no skill defined where that counter lives, what its labels may
contain, or what alert it feeds**. `python-rest-api` listed `structlog` and never said to bind a
request id to it, so the log line a fallback emits could not be tied to the request that caused it.

There is direct evidence the gap changes output: in the A/B trial behind #22, **no arm emitted a
fallback metric** while the rule lived in a principle bullet. It landed only once the increment was
written inside the helper body that gets copied.

## What Changes

- New `skills/observability/SKILL.md` (1.0.0, category `backend`), canonical home for:
  - **Correlation** — accept or generate one id per request, bind it to `structlog` via contextvars,
    return it in the response header, propagate it outbound. `clear_contextvars()` first, because a
    reused worker otherwise leaks the previous request's id, which is worse than none.
  - **RED metrics** — rate, errors, duration per endpoint and dependency, with the cardinality rule
    stated twice because it is the mistake that takes the metrics backend down: label with the route
    template, never a raw path, and never with anything a client controls.
  - **The fallback counter's home** — `op` is the logical operation, `err` is the exception *type*
    (never `str(exc)`, which carries ids and timestamps), alert on the rate.
  - **Health's third state** — liveness, readiness, and *degraded*: serving, on fallbacks, both probes
    green. A body field and a metric, not a status code.
  - **Tracing** — when a request has hops. Make the trace id the request id, or carry both; two
    correlation ids for one request is worse than one.
  - **What not to instrument** — spans per loop iteration, bodies in logs, a metric per business
    entity, debug at INFO.
- `backend-resilience` → 2.0.1 and `python-rest-api` → 1.4.1 link the new skill instead of restating
  it: the counter's definition and the correlation rules move out of their prose and into one place.
- README row in the backend section.

## Verification

Every construct was run before being prescribed, on `fastapi 0.141.1` · `prometheus-client 0.26.0` ·
`structlog 26.1.0` · `opentelemetry-api 1.44.0` · `opentelemetry-instrumentation-fastapi 0.65b0`:

| claim | result |
|---|---|
| request id generated when absent, returned in the header | yes |
| a client-supplied `X-Request-Id` is preserved | yes |
| logs carry `request_id` without the call site passing it | yes |
| the route **template** is the label | `route="/items/{item_id}"` |
| the raw path stays out of the registry | `/items/7` absent from `/metrics` |
| counter, latency histogram and `fallback_used_total` exposed | yes |

## Capabilities

### New Capabilities

- `observability`: correlation, RED metrics, the fallback counter registry, degraded-state reporting
  and tracing adoption for a backend service.

### Modified Capabilities

- `skills-catalog`: the catalog gains `observability`; `backend-resilience` and `python-rest-api`
  delegate to it rather than defining metrics and correlation themselves.

## Impact

- New `skills/observability/`; edits to `skills/backend-resilience/SKILL.md` and
  `skills/python-rest-api/SKILL.md` (links only); README; regenerated wrappers.
- Catalog 31 → 32.
- Closes #49.
