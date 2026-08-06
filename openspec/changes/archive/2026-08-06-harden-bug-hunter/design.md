## Context

`bug-hunter` sits at the centre of the catalog's testing story: `python-rest-api`,
`backend-resilience`, `api-resilience-testing`, `fivem-fallback` and `openspec-drivezone` all defer to
it for what "adversarially tested" means. It had never been tested against anything itself.

The audit that ran across the whole catalog produced a rare opportunity: five defects, each found by a
different instrument (a simulation battery, a FastAPI probe, a TypeScript compile, a live Projects v2
run), none of them found by following this checklist. That makes the checklist falsifiable — score it
against the defects and see what it would have caught.

## Goals / Non-Goals

**Goals**
- Close the classes the checklist provably missed, each traceable to a specific defect.
- Keep the checklist short enough to actually run — it is a rite, not a taxonomy.
- Make the growth mechanism explicit so the next escape widens it too.

**Non-Goals**
- Not turning it into `api-resilience-testing`. That skill owns the exhaustive REST surface audit;
  this one stays per-change and stack-agnostic.
- Not adding items that sound rigorous but have no incident behind them. Every added row names its
  defect; anything without one did not get in.
- Not rewriting the stack tracks. Only their concurrency scenarios changed, to match the burst rule.

## Decisions

**D1 — Score, don't review.** The improvement came from asking "would this have caught X?" for five
concrete X's, not from reading the checklist and imagining gaps. Four clean misses and one wrong-scale
partial is a measurement, and it is the reason each item is here.

**D2 — Distinctness is the item most worth adding.** Idempotency and distinctness are inverses and the
checklist only had one of them. "Run it twice, does it apply once" and "two different things happen to
look the same, do they stay two" fail in opposite directions, and dedup code satisfies the first while
violating the second — which is exactly the bug found in the log collector.

**D3 — Burst replaces pair as the default, pair stays as the floor.** Single-flight, connection-pool
limits and negative caches are all invisible at two callers. The measured case (38 of 200 reaching a
down dependency) only exists above a threshold, so the scenario has to name a scale.

**D4 — Observability is a test, not a nice-to-have.** "Degrades safely" was satisfied by a helper that
also swallowed a `TypeError` from local code with no signal. Asserting the log line and the counter is
what separates a working fallback from a silent one.

**D5 — The table is part of the doctrine, not commentary.** It gives every item provenance and makes
the checklist auditable: an item with no defect behind it does not belong. The standing rule to add a
row when a scenario is added keeps that property.

**D6 — Shape and fragmentation are input-side siblings of existing items.** "Boundaries" covers value
extremes, "partial failure" covers the operation breaking midway. Neither covers a small input with
hostile structure, or an input that is itself incomplete when read. They sit next to their siblings
rather than in a new section.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Per-change adversarial methodology and its universal checklist | `bug-hunter` | already canonical — checklist extended |
| Stack-specific adversarial depth (Python, FiveM/Lua, .NET plugin) | `bug-hunter/references/track-*.md` | already canonical — concurrency scale raised |
| Expected behaviour under "dependency down" (safe default, negative cache, observability) | `backend-resilience` | link (already canonical) — the observability item asserts what it defines |
| Exhaustive REST surface audit | `api-resilience-testing` | link (already canonical, unchanged) |
| The tasks.md gate that consumes this rite | `openspec-drivezone` | unchanged; inherits the wider checklist |

## Risks / Trade-offs

- [The checklist grows and stops being run] → five items on a seven-item list is a real increase; the
  provenance table is the counterweight, since an item nobody can trace gets removed rather than
  tolerated.
- [Burst testing is harder to write than a pair] → yes, and it is the only way the guard is exercised;
  the Python track keeps the pair as the documented minimum for cases where a burst is impractical.
- [The provenance table ages as the defects recede] → it is history, not a claim about the present, and
  it is what stops the checklist filling with plausible-sounding items.
