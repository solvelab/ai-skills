# API Resilience Testing

Test a REST API so it survives the inputs nobody intended — invalid, malformed,
out-of-contract, hostile — and fails **safely** instead of crashing, corrupting
data, or leaking internals. This is the discipline of going **beyond the happy
path**.

## What to call this (terminology)

There is no single industry term; these overlap and are often used together.
Use the umbrella term **API robustness / resilience testing** and name the
sub-disciplines precisely:

| Term | Scope |
|------|-------|
| **Negative testing** | Feed invalid/unexpected input, assert graceful rejection (correct 4xx, no crash). The core of this skill. |
| **Robustness / destructive testing** | Actively try to *break* the API (malformed bodies, type confusion, huge payloads). Negative testing taken to its limit. |
| **Fuzz testing** | Automatically generate massive volumes of random/edge inputs, usually schema-driven, to find unhandled cases (500s, hangs). |
| **Contract testing** | Verify the implementation matches its declared contract (OpenAPI/JSON Schema), or that consumer↔provider expectations hold (Pact). |
| **API security testing** | Authn/authz abuse, injection, SSRF, object-level authorization (OWASP API Top 10). |

**Recommended primary label:** *API robustness testing* (or *resilience testing*).
"Negative testing" is the most precise name for the manual scenario work;
"fuzzing" for the automated generation; reach for the specific term per activity.
Avoid vague "bug hunting" / "QA security testing" in formal docs — they are
informal and ambiguous.

---

## When to use this skill

Trigger whenever the work involves a REST/HTTP API: adding or changing an
endpoint, reviewing an API PR, writing API tests, designing request/response
schemas, or the user asks to "test", "harden", "break", "audit", or "review"
an API. Default to running the workflow below before an API change is
considered done — happy-path tests alone are not sufficient.

---

## The workflow (10 steps)

Run these in order. Produce concrete, runnable tests and a checklist — not prose.

1. **Map the endpoints.** List every route: method, path, auth requirement,
   path/query params, request body, success + error responses. Prefer the
   OpenAPI/Swagger spec if one exists; otherwise derive it from the router and
   handlers. Note which endpoints mutate state (these need rollback/idempotency
   checks) and which return lists (pagination, filtering).

2. **Capture the expected contract.** For each endpoint pin down: required vs
   optional fields, types, formats (email, uuid, date), ranges/lengths, enums,
   the success status code, and the documented error shape. If the contract is
   implicit, make it explicit first — you cannot test against an undefined
   contract.

3. **Design positive + negative scenarios.** One happy path per endpoint, then
   negatives from the catalog below. Cover every required field, every typed
   field, every boundary, every auth state. Prioritize state-mutating and
   auth-protected endpoints.

4. **Try to break it.** Send malformed JSON, wrong types, nulls where not
   allowed, missing required fields, extra/unknown fields, oversized payloads,
   deeply nested objects, wrong/empty/missing `Content-Type`, invalid encodings,
   injection strings, and out-of-range numbers. For unknown-shaped surfaces,
   fuzz from the schema (Schemathesis/RESTler) rather than hand-writing every case.

5. **Validate status codes.** 400 invalid body/params, 401 missing/invalid auth,
   403 authenticated-but-forbidden, 404 unknown resource, 405 wrong method,
   409 conflict, 413 too large, 415 unsupported media type, 422 semantic
   validation, 429 rate limit. A 500 on bad *input* is a bug — input errors must
   be 4xx.

6. **Validate error responses are safe and useful.** Errors must be a consistent,
   machine-readable shape (prefer RFC 9457 `application/problem+json`: type,
   title, status, detail, instance). They must NOT leak stack traces, SQL,
   internal paths, framework versions, or raw exception text. They MUST say
   clearly what was wrong so a client can fix it.

7. **Verify authentication & authorization.** No token → 401. Expired/garbage/
   wrong-signature token → 401. Valid token, insufficient role → 403. Critically,
   test **object-level authorization (BOLA/IDOR)**: user A must not read/modify
   user B's records by guessing IDs — the #1 API risk. Also test mass assignment
   (can a client set fields like `is_admin`, `user_id`, `role` via the body?).

8. **Hunt critical bugs & unexpected behavior.** Watch for: 500s, hangs/timeouts,
   partial writes on error (state changed despite a failure response — the data
   must be unchanged if the call errors), duplicates on retry of a failed call,
   inconsistent error shapes, type coercion surprises, and contract drift (the
   response not matching the schema/OpenAPI).

9. **Suggest automated tests.** Turn the scenarios into code in the project's
   stack (pytest/httpx, Jest/supertest, RestAssured, etc.). Add schema-driven
   fuzzing in CI if an OpenAPI spec exists. Keep them deterministic and fast;
   each negative case asserts both the status code AND the error body shape.

10. **Produce the resilience checklist.** End with the filled checklist below,
    marking pass/fail/gap per item, so coverage is visible and reviewable.

---

## Reusable resilience checklist

Copy this per API/endpoint and mark `[x]` pass, `[ ]` gap.

```
### Input validation
[ ] Missing each required field → 400/422 (not 500)
[ ] Null in non-nullable field → 400/422
[ ] Empty string / whitespace-only where a value is required → rejected
[ ] Wrong type per field (string↔number↔bool↔array↔object) → 400/422
[ ] Out-of-range numbers (negative, zero, max+1, overflow) → 400/422
[ ] Over-length strings / oversized payload → 400/413
[ ] Invalid format (email, uuid, date, enum) → 400/422
[ ] Unknown/extra fields → ignored or rejected (documented, never crash)
[ ] Malformed JSON / truncated body → 400 (not 500)
[ ] Deeply nested / huge array payload → handled, no DoS

### Headers & content
[ ] Missing Content-Type on a body request → 400/415
[ ] Wrong Content-Type (text/plain for JSON) → 415
[ ] Missing required custom headers → handled
[ ] Unsupported Accept → 406 or sane default

### Auth & authorization
[ ] No token → 401
[ ] Malformed / expired / wrong-signature token → 401
[ ] Valid token, insufficient role → 403
[ ] BOLA/IDOR: user A cannot access user B's object by ID → 403/404
[ ] Mass assignment: client cannot set privileged fields via body
[ ] Unauthenticated access to a protected route → 401 (never leaks data)

### Methods & routing
[ ] Wrong HTTP method on a route → 405
[ ] Unknown resource id → 404 (consistent shape)
[ ] Trailing slash / case variations behave consistently

### Status codes & errors
[ ] Input errors are 4xx, never 5xx
[ ] Error body is consistent & machine-readable (ideally RFC 9457)
[ ] No stack trace / SQL / internal path / version leaked in any error
[ ] Error message is actionable (says what to fix)

### State & side effects
[ ] On a failed write, the database is unchanged (no partial commit)
[ ] Retry of a failed mutating call does not duplicate data (idempotency)
[ ] Concurrent identical requests don't corrupt state

### Limits & resilience
[ ] Rate limiting / throttling returns 429 (if applicable)
[ ] Pagination bounds enforced (huge/negative limit/offset)
[ ] Response conforms to the declared schema/OpenAPI (contract not drifted)
```

See `references/negative-test-catalog.md` for concrete request/response examples.

---

## Tools (suggest the lightest that fits)

- **Schema-driven fuzzing:** [Schemathesis](https://schemathesis.io/) — generates
  thousands of cases from an OpenAPI/GraphQL schema (property-based, Hypothesis);
  catches 500s, schema violations, edge cases with almost no code. Best
  first reach when a spec exists.
- **Stateful API fuzzing:** Microsoft **RESTler** — learns producer/consumer
  dependencies from OpenAPI and chains calls; good for workflow bugs.
- **Contract testing:** **Pact** (consumer-driven, microservices), or
  **Dredd**/OpenAPI validators (provider-vs-spec).
- **Security:** **OWASP ZAP** (DAST/active scan), and the
  [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/) as the
  authorization/abuse checklist.
- **Manual & exploratory:** Postman/Newman, `curl`/HTTPie for one-off negatives.
- **In-code tests:** the project's own framework (pytest+httpx, supertest,
  RestAssured) for the deterministic negative cases — these belong in CI.

---

## Integrating into the dev flow (shift-left)

- **Definition of done** for any endpoint = happy path **plus** the negative
  scenarios for its inputs and auth, plus the resilience checklist reviewed.
- **In CI:** run the in-code negative tests on every PR; if an OpenAPI spec
  exists, run Schemathesis against the running app as a gate. Fail the build on
  any 500-from-bad-input or schema nonconformance.
- **In code review:** apply this skill to the diff — for each new/changed
  endpoint, ask "what breaks it?" before approving.
- **Contract as source of truth:** keep the OpenAPI spec accurate; a golden
  snapshot test of the generated schema catches accidental contract drift.
- **Error standard:** adopt one error shape (RFC 9457) repo-wide so clients and
  tests can rely on it and nothing leaks.

---

## Output format

When invoked, produce:
1. A short **best-practices summary** + the correct **terminology**.
2. The **endpoint map** with contracts.
3. **Positive + negative test scenarios** (concrete requests + expected status
   and error shape).
4. **Suggested automated tests** in the project's stack.
5. The filled **resilience checklist** with gaps flagged.
Keep it concrete and runnable; favor real example payloads over description.
