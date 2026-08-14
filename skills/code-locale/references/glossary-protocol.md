# Glossary protocol — decide the name once, at grooming

The rule is in `../SKILL.md`. This file is the mechanism that prevents the defect instead of
catching it.

## Why the glossary exists

The backlog item is written in the repository's working language, and that is correct — humans read
it, sometimes non-engineers. The failure is not the language of the item. It is that **nobody
decides the English name at a point where the decision is cheap**, so the implementing agent mirrors
the item's nouns straight into identifiers while writing code.

The glossary moves that decision to grooming, where it costs one table row and is reviewed by the
person who knows the domain.

## The section, in the item

Produced by `backlog` into every item that will produce code, immediately before
`## Technical requirements` so the technical requirements can cite it:

```markdown
## Glossary (domain term → identifier)

| Termo (PT) | Identifier (EN) | Origin |
|---|---|---|
| pedido | `order` | already used in `app/models/order.py` |
| entrega | `delivery` | new — decided here |
| nota fiscal | `nota_fiscal` | keep-as-is: legal document, no faithful translation |
```

## The Origin column is the load-bearing part

Every row is either **harvested** from the codebase or **decided** in the item. That is what turns
the glossary into evidence rather than a translation exercise, and it enforces the order:

1. **Harvest first.** Search the target repo for what it already calls the concept. A codebase that
   says `order` must not receive a second word for the same thing because an item invented
   `purchase` in isolation. Harvesting is a context-collection step, not a naming step.
2. **Decide only what harvesting did not answer**, and mark the row `new — decided here` so a
   reviewer can see exactly which names are being introduced.
3. **Keep-as-is is a third outcome**, not a failure to decide. The row states the reason, which is
   what makes the term legitimate under the exception gate in `../SKILL.md`.

A term that neither the codebase nor the user can resolve is a **gap question**, asked before the
item is created. It is never a translation invented in the draft — an invented name is an unverified
claim about the domain (`verify-before-claiming`).

## Consumption, during execution

`execute-backlog` reads the glossary and puts it in the plan it presents for approval:

```markdown
**Glossary**: term → identifier (from the item; rows derived here are marked NEW)
```

This is the highest-leverage gate in the whole flow. The plan is already human-approved **before any
file is touched**, so a wrong or missing translation is corrected at the moment it costs nothing —
not after it is spread across a diff, a route, a migration and a dashboard query.

During implementation the glossary is the source of names. A term that appears in the work but not in
the glossary is a stop-and-ask, not an improvisation.

## What the glossary is not

- **Not a dictionary.** It carries the terms this item actually uses, not the domain's whole
  vocabulary. Five rows are normal.
- **Not a rename list.** It names what the item creates. Existing Portuguese identifiers are
  governed by `migration.md`, and appear here only if the item was already going to touch them.
- **Not required for items that produce no code.** A docs-only or process-only item has nothing to
  name.

## Growth

A term decided in one item and used again later is harvested from the codebase by the next item —
the Origin column will say `already used in <path>`. That is the intended steady state: the glossary
stops being authored and starts being read, and the codebase becomes its own dictionary.
