## 1. backend-resilience (2.0.0)

- [x] 1.1 Add ordered doctrine line (timeout → deadline → bounded retry → negative cache +
      single-flight → fallback → surface) and rewrite Principles with: explicit timeout per call,
      wall-clock deadline, retry only idempotent operations, degradation is an observable event
- [x] 1.2 Add "Timeouts and the deadline budget" section with the sizing rule
      (`attempts x timeout + backoff <= deadline <= caller budget`) and the measured worst cases
- [x] 1.3 Rewrite `safe_call` to carry the cause (`err_type`), log it and increment a counter; add
      `safe_call_async`; document why `CancelledError` must keep escaping
- [x] 1.4 Add "Retry: bounded, backed off, jittered" — retryable set (timeouts, resets, 502/503/504,
      429 honoring `Retry-After`), full jitter, no stacked retry layers, retry budget 10-20%
- [x] 1.5 Correct the negative-cache section: single-flight probe guard, jittered fail-TTL, per-key
      cache, with the measured 200-caller numbers; add the circuit-breaker escalation note
- [x] 1.6 Add stale-with-marker rule to "Surface failures" and the degraded-readiness rule
- [x] 1.7 Add "What to test" handoff section pointing at `bug-hunter`
- [x] 1.8 Bump `metadata.version` to 2.0.0 and update the frontmatter description

## 2. log-event-collector (1.1.0)

- [x] 2.1 Replace the `handle.tell()` offset rule with "advance only to the last complete line",
      including the byte-slice snippet and the held-back-remainder cap
- [x] 2.2 Replace the `event_key` formula: occurrence discriminator (log file + byte offset) instead
      of `line_hash(raw_line)`; state the measured collapse
- [x] 2.3 Seen-set becomes set + `deque(maxlen=N)`; state the rotation-guard/replay-window
      interaction and require the project to name its idempotency authority
- [x] 2.4 Backend-client section links `backend-resilience` for retry doctrine; keeps only collector
      specifics (retryable set incl. 429/`Retry-After`, worst case under the poll interval)
- [x] 2.5 Add "Backpressure" and "The collector's own observability" sections
- [x] 2.6 Close the stdlib-only conditional (state the other branch)
- [x] 2.7 Bump `metadata.version` to 1.1.0 and update the frontmatter description

## 3. python-rest-api (1.3.0)

- [x] 3.1 Add "Request limits" rule: max body size (413) + JSON depth guard (400), with the measured
      thresholds (2 KB nested body → 500; 20 MB flat body → 200 on the stock stack)
- [x] 3.2 Add `RecursionError` to the 400 row of the exception-handler table
- [x] 3.3 Require an explicit timeout on every outbound call; link `backend-resilience`
- [x] 3.4 Fix `references/fastapi-envelope.md`: define the missing `ValidationException` (422),
      implement the `APP_ENV == "dev"` branch in the catch-all handler, note the `str(exc)`
      string-sniffing fragility and that the `HTTPException` code map only serves raw raises
- [x] 3.5 Bump `metadata.version` to 1.3.0

## 4. api-resilience-testing (1.2.0)

- [x] 4.1 Correct the checklist status codes to the measured baseline behaviour (malformed JSON 422,
      Content-Type 422, Accept 200, path-param type 422), each noting whether an override is worth it
- [x] 4.2 Resolve the error-shape conflict: "one documented machine-readable shape applied to every
      error path"; RFC 9457 named as the greenfield default, not a requirement; remove the rival
      assertion from step 6 and the "Error standard" bullet
- [x] 4.3 Add the oversized-body and deep-nesting cases to `references/negative-test-catalog.md` with
      the measured evidence, linking the guard to `python-rest-api`
- [x] 4.4 Bump `metadata.version` to 1.2.0

## 5. fivem-fallback (1.3.0)

- [x] 5.1 Bound the shared-client retry: deadline + jitter, and drop the implication that a blind 5xx
      retry is safe for a non-idempotent call
- [x] 5.2 Bound the boot loop with a total deadline; state the measured stacked worst case
- [x] 5.3 Bump `metadata.version` to 1.3.0

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on all five skills: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [x] Q.2 All touched skill content in English (catalog locale)
- [x] Q.3 Description triggers still route correctly for each skill and every "Do NOT use for"
      boundary survives
- [x] Q.4 No duplicated doctrine: retry/timeout/fallback mechanics live only in `backend-resilience`;
      request limits only in `python-rest-api`; siblings link per the design.md Canonical Home table
- [x] Q.5 Every quantified claim added carries its measured number and conditions (skills-authoring:
      Simulated failure behaviour)
- [x] Q.6 README skill-table rows updated for the five skills

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-backend-skills --strict` green
- [x] V.2 `scripts/validate-rite.sh` green (rite gate incl. this change's own gate groups)
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 CI frontmatter check passes locally (name == dir, semver, category, license on every
      `skills/*/SKILL.md`)
- [ ] V.5 `openspec archive harden-backend-skills --yes` after all groups above and after review
