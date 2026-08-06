---
name: bug-hunter
description: >-
  Adversarial testing rite — after implementing a change, actively try to break it instead of only
  confirming the happy path. Use when writing or reviewing tests for a just-implemented change, when a
  tasks.md has a "Testes & Bug-Hunter" group, or when the user says bug hunt, adversarial test, break
  it, anti-forge, or asks to test edge cases/atomicity/races of a specific change. Stack-agnostic
  methodology with opt-in stack tracks in references/ (Python/pytest, FiveM/Lua, .NET plugin loaded
  by a host runtime). Do NOT use for designing a full API test suite from scratch — that is
  api-resilience-testing.
metadata:
  author: solvelab
  version: 2.2.0
  category: testing
license: MIT
compatibility: Works in any environment with filesystem access.
---

# Bug-Hunter — adversarial testing

A repeatable rite: after implementing a change, actively **try to break it** — don't just confirm the
happy path. Hunt for the bug before it ships.

## Mindset

- Assume the input lies, the dependency fails, and two things happen at once.
- For each invariant the code relies on, write a test that **violates** it and assert it's rejected.
- A green happy-path test proves nothing about forged input, partial failure, or concurrency.

## Universal checklist (any change, any stack)

- **Boundaries**: zero, negative, max, just-over-max, empty, null/None, wrong type.
- **Shape, not just size**: a *small* input with a hostile *structure* — 1000 levels of nesting, a
  deeply recursive object, a self-referencing graph. Size limits do not catch these.
- **Fragmented input**: the input arrives in pieces — a line still being written, a chunked body, a
  message split across packets. Does a reader that lands mid-write consume half of it and advance?
- **Forged input**: ids/owners that belong to someone else; values the client shouldn't be able to set.
- **Idempotency / replay**: run the same operation twice — does it apply/charge exactly once?
- **Distinctness** (the inverse, and the one that gets forgotten): two *genuinely different*
  occurrences that happen to look identical — same payload, same second, same key material. Do they
  stay two? A dedup key built from content instead of position collapses them and silently drops one.
- **Partial failure**: make a mid-operation step fail — does everything roll back (no partial effect)?
- **Dependency down**: external service times out / 5xx / returns garbage — does it degrade safely?
  (Expected behavior is defined by `backend-resilience`: safe default, negative cache, no silent stale.)
- **Observable degradation**: when it *does* degrade safely — can anyone tell? Assert the log line and
  the counter, not just the fallback value. A helper that returns the default for a timeout and for a
  `TypeError` in your own code, with no signal, is indistinguishable from working.
- **Concurrency at burst, not in pairs**: two requests at once is the *cheapest* case, not the
  representative one. Fire N (100+) and count how many reached the dependency. Guards like
  single-flight are invisible at two callers and decisive at two hundred.
- **Regression**: the related existing suite still passes with the new guard on.

### Why these five were added

Each came from a defect found by other means, that this checklist as written would have missed:

| Added item | The bug it would have caught |
|---|---|
| Shape, not just size | a 2 KB body of nested brackets returning **500** from a stock API — every value-boundary case passed |
| Fragmented input | a log line arriving across two write flushes: the tailer consumed the half-line and advanced past it, producing two bogus events and zero correct ones |
| Distinctness | two real reconnects with a byte-identical log line collapsing to one dedup key — the second event silently dropped |
| Observable degradation | a fallback helper folding four distinct failure causes into one silent return, with zero log lines |
| Burst, not pairs | 200 concurrent callers against a down dependency: **38** still paid the full timeout; at two callers the missing guard is invisible |

When you add a scenario because something escaped, add the row too. A checklist that never grows is a
checklist that stopped finding things.

## Stack tracks (read the one that matches what you changed)

- **Backend REST (Python/pytest example stack)** → `references/track-python-pytest.md`
- **FiveM/Lua** → `references/track-fivem-lua.md`
- **.NET plugin loaded by a host runtime** (AssettoServer-style) → `references/track-dotnet-plugin.md`
- Other stacks: apply the universal checklist with the same rigor; the tracks show the expected depth.

## Output

List each hunted scenario as a test (automatable stacks) or as a checklist item + documented smoke test
(where no headless runtime exists). A change isn't done until its Bug-Hunter group is green/checked.
This pairs with the OpenSpec `tasks.md` "Testes & Bug-Hunter" gate used by `openspec-drivezone`.

## See also

- `api-resilience-testing` — full REST negative/fuzz/contract/security methodology and checklist; use
  it when the target is an API surface, not a single change.
- `backend-resilience` — the fallback behavior these tests assert.
- `fivem-lua` — the trust-boundary rule (`source`, not client args) that the Lua track exercises.
