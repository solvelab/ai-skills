# Migration — English from here; rename on touch; contracts get a window

The rule is in `../SKILL.md`. This file governs code that already exists.

**A rule that turns a legacy codebase red on day one is a rule that gets `--no-verify`'d out of
existence in a week.** Everything below follows from that.

## Tier 1 — new code is English

Enforced mechanically, over added lines only:

```bash
git diff origin/main... | python3 check-identifier-locale.py --diff -
```

Wire this into pre-commit and CI. Whole-tree scanning is for a repository that is already clean, not
for adoption.

## Tier 2 — internal names are renamed opportunistically

Locals, private functions, non-exported types, internal modules: renamed **when the file is already
being changed for another reason**, and in a **separate `♻️ refactor` commit** so review can read
behaviour and rename independently. Never a standalone rename sweep.

Bounded to what the diff already touches. A file nobody had a reason to open is not a reason to open
it.

## Tier 3 — contract-bearing names are never renamed in place

A name is contract-bearing when something outside the module reads it: REST paths and query params,
JSON body fields, DB columns, event/topic names, persisted enum values, deployed config keys, and log
field keys consumed by dashboards or alert rules.

Expand/contract, with a parallel-run window:

1. **Add** the English name alongside the old one.
2. **Serve and accept both.**
3. **Instrument** usage of the old name.
4. **Remove** it after observed usage is zero for a stated window.

`python-rest-api` already documents this shape as rollout-gated enforcement (log-then-enforce); use
that mechanism rather than inventing a second one.

A column rename is `ADD column → backfill → dual-write → switch reads → drop`, never
`ALTER TABLE ... RENAME COLUMN`.

Each tier-3 rename is its own backlog item, with the deprecation window written into its acceptance
criteria.

## Never a big-bang rename PR

It destroys `git blame`, conflicts with every open branch, and is unreviewable at size. The decisive
argument in this stack is different, though: **Lua, JavaScript and SQL reference names as strings.**

Every dynamic reference a mechanical rename misses fails silently at runtime, with no compiler to
catch it — NUI message names, FiveM event strings, `exports` lookups, raw SQL in an ORM, Grafana and
Loki queries, Consul keys, Helm values, `getattr` and table-key construction.

A rename that crosses a wire boundary is a **compatibility change**, not a refactor. Test the old
name's clients before removing it — the adversarial method for that is `bug-hunter`.

## The allowlist is the debt ledger

`.identifier-locale-allow` at the repository root, one token per line, `#` for comments:

```
# grandfathered 2026-08-14 — tier 3, awaiting deprecation window
pedidos
situacao

# permanent — Brazilian legal instrument, see code-locale
nota_fiscal
```

Two entries with very different meanings, and the comment is what separates them:

- **Grandfathered** legacy names, which are debt. `wc -l` of this file per release is the migration
  metric, and it shrinks only through tier-2 and tier-3 work.
- **Permanent** domain terms, which are not debt and never shrink.

Prefer the inline `locale-ok: <reason>` waiver for permanent exceptions, because it sits next to the
code a reviewer is reading. Reserve the file for legacy names that appear in too many places to
annotate individually.

## Recording adoption

The policy lives here, once. Each repository records its own state in two places: a short section in
its `CONTRIBUTING.md` or an ADR, and its `.identifier-locale-allow`. Wiring the detector into a
repository's CI and seeding its allowlist is one backlog item per repository, not a catalog change.

## The trade this policy accepts

`--diff` mode gives weaker coverage than a full-tree scan: a Portuguese identifier already in the
tree is invisible until someone edits that line. That is deliberate, and it is the price of a rule
teams actually keep. The alternative — a red pipeline on day one — buys stronger coverage on paper
and none in practice.
