# Change: Harden the backend skill family against measured failure modes

## Why

A simulation battery run against the code the backend skills actually prescribe (2026-08-06, this
repo) reproduced three defects and six gaps in doctrine that is presented as production-hardened:

- `log-event-collector` ends its tail loop with `handle.tell()`. A log line arriving across two write
  flushes is consumed half-read and the offset advances past it: measured, one line produced two
  bogus events and zero correct ones.
- `log-event-collector`'s `event_key` hashes the raw line, so two genuinely distinct occurrences of a
  byte-identical line collapse to one key and the second real event is silently dropped.
- A stock FastAPI service — the `python-rest-api` baseline — answers **HTTP 500** to a 2 KB request
  body of nested brackets (`RecursionError`), and **HTTP 200** to a 20 MB body. Both skills declare
  a 5xx from bad input to be a bug; neither prescribes the body-size or depth limit that prevents it.
  Verified against fastapi 0.141.1 / pydantic 2.13.4, and the mitigation verified to return 400/413.
- `backend-resilience`'s negative cache has no single-flight guard: measured, 200 concurrent callers
  against a down dependency still paid 38 full timeouts. With the guard, 1.
- No skill states a wall-clock deadline, only attempt counts. The policies as written reach a 50s
  worst case (`fivem-fallback`, 10 attempts) and ~18 minutes when stacked under its own boot loop.
- `safe_call` swallows four distinct failure causes into one indistinguishable outcome and emits no
  log, contradicting its own principle "never silent stale state".

An A/B trial (two arms per side, same task, same reference file) measured what the doctrine actually
produces: the current `backend-resilience` yielded 10.5/17 of the target behaviours, a revised draft
yielded 16/17. The five behaviours gained — connect/read timeout split, exponential backoff, retry
jitter, wall-clock deadline, fail-TTL jitter, `Retry-After` — are exactly the ones the current text
does not mention. No arm emitted a fallback metric, so that rule needs to be structural, not a
principle bullet.

`api-resilience-testing` also asserts status codes the baseline stack does not produce (malformed
JSON → 400; FastAPI returns 422), and prescribes RFC 9457 while `python-rest-api` prescribes a custom
envelope — the two skills cite each other and disagree.

## What Changes

- `backend-resilience` → 2.0.0: add explicit-timeout and deadline-budget doctrine, retry
  classification with exponential backoff + full jitter + `Retry-After` + retry budget, the
  idempotent-only retry rule, single-flight on the negative-cache probe, fail-TTL jitter, an async
  helper variant, cause-carrying + counted fallbacks, a circuit-breaker escalation note, and a
  "what to test" handoff to `bug-hunter`.
- `log-event-collector` → 1.1.0: fix the partial-line offset rule and the `event_key` formula, switch
  the seen-set to set+deque and state the replay-window interaction with the rotation guard, link
  retry doctrine to `backend-resilience` instead of restating it, add backpressure and
  collector-self-observability sections, close the stdlib-only conditional.
- `python-rest-api` → 1.3.0: add a request-limits rule (max body size + JSON depth, with the measured
  numbers), map `RecursionError` to 400 in the handler table, define `ValidationException` (named in
  the doctrine, missing from the reference drop-in), implement the `APP_ENV == "dev"` branch the
  doctrine promises, flag the `str(exc)` string-sniffing fragility, and require an explicit timeout on
  every outbound call.
- `api-resilience-testing` → 1.2.0: correct the asserted status codes to what the baseline stack
  returns, resolve the error-shape conflict in favour of the documented envelope (RFC 9457 stays as
  the greenfield default, not a requirement), and add the oversized/deeply-nested body cases with the
  measured evidence.
- `fivem-fallback` → 1.3.0: bound the 10-attempt retry with a deadline and jitter, and stop implying
  a blind retry is safe for non-idempotent calls.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — a skill's claims about runtime failure behaviour SHALL be
  backed by a reproducible simulation, and prescribed code SHALL be exercised against the failure it
  claims to handle before publication.

## Impact

- Skills: `backend-resilience`, `log-event-collector`, `python-rest-api`, `api-resilience-testing`,
  `fivem-fallback` (+ `references/fastapi-envelope.md`), and every regenerated wrapper tree
  (`claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`).
- README skill table rows for the five skills.
- Consumers: services built on `python-rest-api` gain two new required guards (body-size limit, depth
  limit); the retry-policy changes tighten previously unbounded attempt counts.
