## Context

The backend family is written around failure: `backend-resilience` degrades safely, `python-rest-api`
never returns a raw 500, `log-event-collector` keeps shipping through an outage. Every one of those
behaviours is invisible from outside the process, and no skill said how anyone would know.

The gap was not theoretical. `backend-resilience` already told the shared helper to increment a
counter — a counter with no defined name, registry or label rules anywhere in the catalog.

## Goals / Non-Goals

**Goals**
- One canonical home for correlation, metrics and degraded-state reporting.
- Every construct probed before it is prescribed.
- The siblings that already reference these ideas link here instead of half-defining them.

**Non-Goals**
- No vendor. Prometheus and OpenTelemetry appear because they are the de facto shapes, and the skill
  says the rule is the shape, not the product.
- No dashboards or alert routing — that is deployment, not doctrine.
- No throughput or overhead benchmarks. The claims here are about what exists in the registry and what
  appears on a log line, which are checkable in seconds.
- Not the collector's own instrumentation; `log-event-collector` owns that and the description says so.

## Decisions

**D1 — Order the skill by payoff: correlate, count, trace.** A request id costs one middleware and
makes every log line already being written useful. Tracing costs a collector and answers questions a
single-service system cannot yet ask. Presenting them as equals pushes readers into the expensive one
first, which is the standard failure of observability advice.

**D2 — State the cardinality rule twice, in two forms.** Once as correctness (a route template is one
series, a raw path is one per value) and once as security (a client-controlled label is a
denial-of-service vector against your own metrics backend). It is the mistake that takes the backend
down, and the second framing is the one that makes people act.

**D3 — Prove the cardinality guard rather than assert it.** The skill records that a request to
`/items/7` produced `route="/items/{item_id}"` and that the string `/items/7` appears nowhere in
`/metrics`. That is a claim a reader can refute in one command, unlike "use the route template".

**D4 — Put the metric where the code is copied from.** The A/B trial behind #22 showed no run emitting
the fallback counter while the rule lived in a prose bullet; it landed once the increment was inside
the helper body. This skill defines the counter, and `backend-resilience` keeps the increment inside
the helper. Definition and usage are deliberately in different places, for that reason.

**D5 — Name the third health state.** `python-rest-api` has liveness and readiness. A service running
entirely on hardcoded fallbacks passes both. "Degraded" is a body field and a metric rather than a
status code, because it must not fail a probe — it must be *visible*.

**D6 — Be honest about tracing's ceiling.** The value is usually the ids and the setup, not the span
tree. Saying so keeps the skill from selling the most expensive part hardest.

**D7 — `err` is the exception type, never the message.** `str(exc)` carries ids, hosts and timestamps,
so one distinct series per occurrence — the cardinality trap arriving through the error path, which is
exactly when nobody is watching the metrics backend.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Correlation ids, RED metrics, label cardinality, degraded reporting, tracing adoption | `observability` | establish here (new) |
| What to do when a dependency fails; the fallback helper that increments the counter | `backend-resilience` | already canonical — now links here for the counter's definition |
| Service baseline: envelope, two-tier health, middleware stack | `python-rest-api` | already canonical — now links here for correlation and the degraded state |
| Asserting the log line and the counter, not just the fallback value | `bug-hunter` | link (already canonical) — its Observable degradation class |
| A log-shipping sidecar's own lag and error counters | `log-event-collector` | unchanged; excluded in this skill's description |

## Risks / Trade-offs

- [Overlap with `backend-resilience`] → the line is stated in both: resilience says what to do on
  failure, observability says how anyone knows it happened. The counter is prescribed there, defined
  here, and neither restates the other.
- [Vendor shapes date] → pinned to probed versions, and the skill says the rule is the shape.
- [Another skill in a family already at five] → it earns its place: without it, three of the others
  prescribe actions whose mechanism is undefined.
