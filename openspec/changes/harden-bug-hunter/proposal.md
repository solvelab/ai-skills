# Change: Add to bug-hunter the five defect classes it demonstrably missed

## Why

`bug-hunter` is the catalog's adversarial-testing rite — the skill every other one defers to for
"did you try to break it". It was used as the testing doctrine throughout a catalog-wide audit that
found five real defects by other means. Scoring those defects against its own universal checklist,
**it would have caught at most one**:

| Defect found | Nearest checklist item | Verdict |
|---|---|---|
| A 2 KB body of nested brackets returns **500** from a stock API | *Boundaries: zero, negative, max, just-over-max, empty, null, wrong type* | miss — every item is a **value** boundary; this is a **shape** boundary at trivial size |
| A log line arriving across two write flushes: the tailer consumed the half-line and advanced past it (2 bogus events, 0 correct) | *Partial failure: make a mid-operation step fail* | miss — that is **your operation** failing midway, not **the input** arriving midway |
| Two real reconnects with a byte-identical log line collapsed to one dedup key; the second event silently dropped | *Idempotency / replay: run the same operation twice — does it apply exactly once?* | miss — it asks the **opposite** question. Nothing tests that two distinct things stay distinct |
| A fallback helper folded four distinct failure causes into one silent return, zero log lines | *Dependency down: does it degrade safely?* | miss — it **did** degrade safely; the defect is that nobody could tell |
| 200 concurrent callers against a down dependency: **38** still paid the full timeout | *Concurrency: **two** requests at once* | partial — right category, wrong scale. At two callers the missing single-flight guard is invisible |

The stack tracks do not close the gap: `track-python-pytest.md` also said "two concurrent requests",
and `track-fivem-lua.md` "concurrent writers", with nothing on distinctness, fragmented input, shape
exhaustion or observability.

A rite that misses the defects found while following it is the highest-leverage thing in the catalog
to fix, because every other skill's testing gate points at it.

## What Changes

- `bug-hunter` → 2.2.0. Five items added to the universal checklist:
  - **Shape, not just size** — a small input with a hostile structure (deep nesting, recursive graph).
  - **Fragmented input** — input arriving in pieces; does a reader landing mid-write consume half?
  - **Distinctness** — the inverse of idempotency: two genuinely different occurrences that look
    identical must stay two. A dedup key built from content instead of position collapses them.
  - **Observable degradation** — when it degrades safely, assert the log line and the counter, not
    only the fallback value.
  - **Concurrency at burst, not in pairs** — fire N (100+) and count how many reached the dependency.
- A **"Why these five were added"** table, mapping each new item to the defect that earned it, plus
  the standing rule: when a scenario is added because something escaped, add its row too.
- `references/track-python-pytest.md` and `references/track-fivem-lua.md`: concurrency scenarios
  raised from a pair to a burst, keeping the pair as the minimum case.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — a skill that prescribes a checklist SHALL be scored against
  defects found in the field, and any class it missed SHALL be added with the defect that earned it.

## Impact

- `skills/bug-hunter/SKILL.md` and both stack-track references; regenerated wrappers.
- Every skill whose testing gate defers to `bug-hunter` — `python-rest-api`, `backend-resilience`,
  `api-resilience-testing`, `fivem-fallback`, `openspec-drivezone` — inherits the wider checklist
  without changing.
- No README change: the skill's purpose and triggers are unchanged.
