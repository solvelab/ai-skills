## Context

The backend family (`python-rest-api`, `backend-resilience`, `log-event-collector`,
`api-resilience-testing`, `bug-hunter`, plus the `fivem-fallback` adaptation) is the most cross-linked
cluster in the catalog: each skill delegates to the others rather than restating. That makes a defect
in one of them propagate — `bug-hunter`'s "dependency down" scenario asserts behaviour *defined by*
`backend-resilience`, so a gap there is a gap in the test rite too.

The skills were written from real production incidents and read as complete. The question this change
answers is not "are they plausible" but "does the code they prescribe survive the failure it claims to
handle". That was measured, not argued: a simulation battery re-implemented each prescribed snippet
verbatim and attacked it, and an A/B trial measured whether the doctrine changes what an agent writes.

## Goals / Non-Goals

**Goals**
- Every failure-behaviour claim in the backend family is backed by a reproducible run.
- Remove the two reproduced defects and the cross-skill contradiction on error shape.
- Close the doctrine gaps the A/B trial proved do not land today (timeouts, deadline, jitter,
  `Retry-After`, fallback metrics).

**Non-Goals**
- No migration to RFC 9457. The documented envelope stays canonical (owner decision, 2026-08-06);
  RFC 9457 is retained only as the greenfield default.
- No new skill. Observability, async/DB concurrency and background jobs are real gaps in the family
  but are separate proposals — this change only adds the observability hooks the measured failures
  require.
- No changes to services built on these skills; this is catalog-only.

## Decisions

**D1 — Retry doctrine is ordered, not a list.** The skill now prescribes
timeout → deadline → bounded retry → negative cache + single-flight → fallback → surface, because the
measured failures were ordering failures: a retry policy with no deadline reached 18 minutes, and a
negative cache with no single-flight let 38 of 200 concurrent callers through.

**D2 — Fallback observability is a rule, not a principle.** In the A/B trial no arm emitted a metric
when the rule lived only in a principle bullet, though the arm that saw a named helper reproduced the
helper. The counter therefore ships inside the prescribed `safe_call` body, where it is copied.

**D3 — Error shape: the documented envelope stays canonical.** `api-resilience-testing` asserted RFC
9457 while `python-rest-api` prescribes `{status, code, message, path, details}`; the checklist marked
a compliant service as failing. The checklist item becomes "one documented, machine-readable shape,
applied to every error path" with RFC 9457 named as the greenfield default. Migration cost for
`react-api-client` and live services is the reason.

**D4 — Status-code assertions follow the baseline stack.** Measured on fastapi 0.141.1: malformed
JSON → 422 (not 400), missing/wrong `Content-Type` → 422 (not 415), unknown `Accept` → 200 (no 406),
wrong path-param type → 422 (not 404). The checklist states the framework-real code, and flags the
ones worth overriding rather than asserting a code the stack never returns.

**D5 — Request limits belong to `python-rest-api`, not to the testing skill.** The 2 KB → 500 defect
is a property of the service baseline; `api-resilience-testing` gains the *test case*, the baseline
gains the *guard*. Single canonical home preserved.

**D6 — `log-event-collector` links retry doctrine instead of restating it.** Per skills-authoring,
fallback/retry is canonical in `backend-resilience`; the collector keeps only its own specifics
(what a collector considers retryable, and the poll-interval constraint).

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Timeouts, deadline budget, retry classification, backoff + jitter, retry budget | `backend-resilience` | establish here (new); `fivem-fallback` and `log-event-collector` link |
| Negative cache + single-flight + fail-TTL jitter | `backend-resilience` | already canonical — corrected in place |
| Fallback observability (cause-carrying log + counter) | `backend-resilience` | establish here; inside the shared helper |
| HTTP request limits (max body size, JSON depth) | `python-rest-api` | establish here; `api-resilience-testing` links the test case |
| Error envelope shape + response codes | `python-rest-api` | already canonical — `api-resilience-testing` stops asserting a rival shape |
| REST negative-testing checklist | `api-resilience-testing` | already canonical — status codes corrected |
| Adversarial methodology | `bug-hunter` | link (already canonical, unchanged) |
| Log tailing, offsets, event dedup | `log-event-collector` | already canonical — defects corrected |
| Trust boundary (`source`, not client args) | `fivem-lua` | link (already canonical, unchanged) |

## Risks / Trade-offs

- [`backend-resilience` grows past a comfortable skim length] → the retry/timeout mechanics stay in
  SKILL.md because the A/B trial shows they only land when inline; the production Consul
  implementation stays in `references/`.
- [Two new required guards in `python-rest-api` (body size, depth) are breaking for existing services]
  → both are additive middleware/handler registrations with a verified happy-path pass; the skill
  states the measured thresholds so adopters can size them.
- [Corrected status codes could read as "lowering the bar"] → each corrected item names the
  framework-real code AND whether overriding it is worth doing, so the checklist still drives a
  decision instead of asserting a false failure.
- [Version bumps invalidate cached copies for adopters] → intended; `backend-resilience` takes a major
  (2.0.0) because the retry rules tighten previously permitted policies.
