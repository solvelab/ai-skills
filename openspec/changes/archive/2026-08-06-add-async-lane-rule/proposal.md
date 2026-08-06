# Change: State the async/sync lane rule for DB access in python-rest-api

## Why

Executes solvelab/ai-skills#50. `python-rest-api` prescribed a **synchronous** SQLAlchemy session while
its own prescribed code ran on the async path, and never mentioned the interaction.

Measured in the file before this change:

| line | content | kind |
|---|---|---|
| 29 | stack lists `pytest-asyncio`, `httpx` | async-capable |
| 110 | `async def dispatch(self, request, call_next)` — the body-limit middleware | **async** |
| 117 | `async def too_deep(request, exc)` — the RecursionError handler | **async** |
| 139 | `Session(engine)` per request via `get_session` | **sync** |

Occurrences of `AsyncSession`: **0**. Occurrences of `event loop`: **0**.

The gap got wider when #22 added an `async def` middleware and an `async def` exception handler to the
same file — the skill now shipped async code sitting next to sync data-access doctrine with nothing
connecting them. A reader can pick `async def` for an endpoint because the examples are async, open a
sync `Session` because the DB section says to, and serve one request at a time with no error and no
log line saying why.

The claim was measured rather than asserted. 10 concurrent 50 ms "queries" via `asyncio.gather` on
Python 3.14:

| shape | wall clock | |
|---|---|---|
| blocking call inside `async def` | **501 ms** | perfectly serialized, ~10x the cost of one |
| the same work awaited | **50 ms** | concurrent |

**10x**, and it grows with concurrency.

## What Changes

- `python-rest-api` → 1.4.0. New section **Async or sync — pick one lane per endpoint**, placed above
  the DB section it qualifies:
  - the rule: never `async def` + a synchronous `Session`, with the measured numbers
  - the two coherent lanes in a table (`def` + `Session` in a threadpool; `async def` + `AsyncSession`)
    and why the sync lane is the right default
  - the trap named explicitly: the middleware and exception handlers this skill prescribes are
    `async def` because Starlette requires it — that does not make the endpoints async
  - what the async lane changes: `create_async_engine`, `async_sessionmaker`, an async `get_session`,
    awaited repositories, and `asyncio_mode = "auto"` for `pytest-asyncio`
  - the failure that survives a green suite: a sync session override in a fixture keeps passing,
    because one test never has concurrency — the block only appears under load
  - the outbound half links `backend-resilience` (`safe_call` / `safe_call_async`), same rule
- The DB section's first bullet now names its lane instead of reading as the only option.
- Description names the lane rule.
- Verified against `SQLAlchemy 2.0.51` and `pytest-asyncio 1.4.0`, both probed.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Simulated failure behaviour** — a claim about a performance or
  concurrency property must be measured and its conditions stated, not asserted from the mechanism.

## Impact

- `skills/python-rest-api/SKILL.md`, regenerated wrappers.
- A service built from the skill can no longer land in the mixed lane by following the examples.
- Closes #50.
