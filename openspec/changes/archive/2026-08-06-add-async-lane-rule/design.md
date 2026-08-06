## Context

`python-rest-api` is the baseline `api-resilience-testing` and `bug-hunter` assume, so a silent
performance trap in it propagates. The trap was not introduced by the skill's author — it appeared when
#22 added async middleware and an async exception handler beside a sync data-access section, and
nothing in the file connected the two.

## Goals / Non-Goals

**Goals**
- State the rule that prevents the mixed lane, with a measurement behind it.
- Give the async lane enough detail to follow, including the test setup.
- Keep the sync lane as the default it deserves to be.

**Non-Goals**
- Not migrating anything. This is doctrine.
- Not advocating async. The mixed lane is the defect; the sync lane is fine and cheaper.
- Not quoting throughput benchmarks. The defensible claim is about blocking, which is mechanical and
  measurable in seconds; a "3-5x more requests/sec" figure from a blog post is not reproducible here
  and was deliberately left out.

## Decisions

**D1 — Measure the blocking, do not assert it.** "A sync call blocks the event loop" is true and easy
to state, and easy to ignore. 501 ms against 50 ms for the same ten calls is not. The measurement is
ten lines of `asyncio` and the skill records its conditions so a reader can rerun it.

**D2 — Name the sync lane the default.** Most services here are DB-bound and already sync; FastAPI's
threadpool for `def` endpoints is a real solution, not a fallback. Presenting async as the goal would
push readers into the harder migration for no gain.

**D3 — Call out the middleware trap by name.** The most likely path into the mixed lane is imitation:
the reader sees `async def dispatch` and `async def too_deep` in this very skill and concludes the
codebase is async. Starlette requires those to be async; endpoints are unaffected. Saying so where the
rule is stated costs two sentences and removes the trap.

**D4 — Document the test failure, not just the runtime one.** A sync session override in an async
fixture keeps a suite green because a single test has no concurrency. That is the reason this defect
reaches production: the suite agrees with the mistake.

**D5 — Place the section above the DB section, not inside it.** The rule governs which lane the DB
prescription belongs to, so it has to be read first. The DB section's first bullet now names its lane
rather than presenting itself as the only option.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| API layering, session-per-request, transactions | `python-rest-api` | already canonical — lane rule added above the DB section |
| Sync vs async helpers for outbound calls | `backend-resilience` | link (already canonical) — same rule, HTTP half |
| Adversarial testing of concurrency | `bug-hunter` | link (already canonical) — its burst class is how you would catch this |
| Measurement discipline for performance claims | `openspec/specs/skills-authoring` | spec delta |

## Risks / Trade-offs

- [The measurement uses `time.sleep`, not a real driver] → deliberately: it isolates the property
  under test (a blocking call in a coroutine) from driver and network noise. The conditions are stated
  so the reader can substitute a real query.
- [Readers may take the async lane as an endorsement] → the table names the sync lane the default and
  says when async earns its cost.
- [The async lane section could rot as SQLAlchemy moves] → pinned to the probed versions.
