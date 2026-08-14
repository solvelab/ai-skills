## Context

`openspec/specs/skills-authoring` carries one language rule — *English as catalog locale*: "All
skill content SHALL be written in English." Its scenario is about a project-specific skill keeping
English prose "regardless of the project's working language". It binds the **author of a skill**
writing **documentation**. Nothing in the catalog binds the **name of a thing in code**.

The evidence that the second half is missing is mechanical, not editorial. Probed at HEAD `429d127`
on 2026-08-14 over 33 skills:

```
$ grep -rniE "identifier language|english identifier|nome em ingl|identificador" skills/ | wc -l
0
$ grep -rnE '"/[a-z0-9_-]*(usuarios|clientes|pedidos|jogadores|veiculos|corridas|produtos|vendas)' skills/ | wc -l
0
```

The catalog's own examples are clean, so this is not a remediation. It is a rule that never existed,
in a catalog whose other instructions actively teach the opposite conclusion: three skills tell the
agent to match the repository's working language without saying that the instruction covers prose
only, and `conventional-commit` names Portuguese as the solvelab default while its only worked
example block is entirely Portuguese.

## Goals / Non-Goals

**Goals:**

- One canonical, stack-agnostic home for the boundary between the prose layer and the machine layer,
  stated so that it cannot be misread as "everything must be English" — that misreading would
  trample `conventional-commit/SKILL.md:30-31`, which is correct and stays.
- Prevention at the point where the translation decision is actually available: grooming. The item
  carries the PT→EN glossary; the implementer never improvises a name.
- A detector precise enough to run in CI. A false positive that blocks a pipeline destroys trust in
  the rule faster than the rule can establish it.
- A migration policy that a legacy codebase can adopt on day one without turning red.

**Non-Goals:**

- Making issues, commits, PRs, docs or code comments English. They are read by humans, sometimes
  non-engineers; that rule is right and is untouched.
- Renaming any existing Portuguese identifier in any repository. The policy is new-code-only, and
  the detector's `--diff` mode encodes it mechanically rather than aspirationally.
- Wiring the detector into any target repo's CI. Adoption is per repo, with its own backlog item.
- Resolving the inert `shared/conventions/` directory. Noticed while designing this change; recorded
  as a follow-up in `tasks.md` E.4, not performed here.

## Decisions

**The name is `code-locale`.** `english-identifiers` was rejected: it is precise but names only half
the rule and invites exactly the "everything English" misreading that would collide with the
Portuguese commit convention. `ubiquitous-language` was rejected as DDD jargon nobody types — skill
routing is driven by the description, but the name still has to be guessable. The name has to signal
*which language goes where*, not *English wins*.

**The rule is scoped by what parses the artifact, not by who wrote it.** A commit body and a code
comment have the same audience, so they land on the same side; a route segment and a DB column have
no audience at all, so they land on the other. This is the only cut that produces a boundary a
reviewer can apply without a taste debate.

**Brazilian legal terms are kept, and the exception is gated.** A CPF is not a "tax id"; a Nota
Fiscal is a SEFAZ document with statutory semantics; `boleto` denotes an instrument no English word
names. Inventing `taxpayerRegistryNumber` destroys traceability to the law, to the regulator's
schema and to the payment provider's API, and guarantees two developers invent two different
translations. The grounding is DDD's ubiquitous language: the shared vocabulary covers domain
*terms*, and says nothing about plumbing verbs — `criarPedido`, `buscarUsuarios`, `salvarDados`
translate the plumbing, which carries zero domain meaning, and that is precisely what leaked.

The gate on the exception is load-bearing and is the most important decision in the design: a kept
term is legitimate **only** when the item's Glossary lists it or the code carries
`locale-ok: <reason>`. Without it, "it is a domain term" is an unlimited escape hatch and the rule
means nothing. Requiring a reason also makes every exception visible in code review.

**The glossary lives in the backlog item, not in the skill.** The leak is not that the issue is
Portuguese — it is that nobody decided the English name at a point where the decision was cheap. The
Origin column ("harvested from `app/models/order.py`" / "decided here") is what turns the glossary
into evidence rather than a translation exercise, and harvesting first is what stops the item
inventing a second English word for a concept the code already names.

**The highest-leverage gate is the approval-gated plan, not CI.** `execute-backlog` already stops
for human approval before touching a file. Putting a `**Glossary**` line in that plan format means
the translation decision is reviewed at the moment it costs nothing to change. CI is the backstop
for what escapes review, not the primary mechanism.

**One detector implementation, two consumers.** The script ships inside
`skills/code-locale/references/` so it travels with the skill install — precedent:
`skills/claude-statusline/references/statusline.sh`. `scripts/validate-skills.py` check C9 shells out
to that same script rather than importing it: shell-out is the idiom the file already uses
(`bash -n`, `luac -p`, `python -c ast.parse` are all subprocesses), it avoids `importlib` path games,
it keeps one lexicon, and it makes the catalog's own CI prove that the script target repos are told
to wire in actually runs — which is what *Verified enforcement claims* requires.

**Precision comes from scope reduction, not from the word list.** Tier 0 does the work: strip
comments and non-path string literals, re-add only machine-layer literals (path-shaped literals and
DDL fragments), extract identifiers, segment them by case convention, match whole segments only,
drop segments under four characters. Whole-segment matching is what eliminates the `validar`/
`validate` and `criar`/`create` class entirely; the 4-char floor eliminates `ma`, `id`, `de`, `os`.
Only then do the four tiers run: non-ASCII letter in an identifier → Portuguese morphology →
Portuguese verb heads → curated Portuguese noun lexicon.

**The lexicon may contain no word that is also an English word.** The script asserts at import that
`LEXICON ∩ ENGLISH_COLLISIONS == ∅` (`data`, `total`, `real`, `local`, `custom`, `nota`, `valor`, …),
so a future contributor cannot quietly add `data` and turn the gate into noise. Suffixes `-mento`,
`-dor` and `-vel` were designed in and then removed for English collisions (`memento`, `vendor`,
`level`) — a CI blocker on `vendorId` would end the rule in a week. They are declared as escapes
instead.

**Untagged code fences are excluded, by design.**
`skills/conventional-commit/SKILL.md:108-119` is an untagged fence of Portuguese commit examples that
must not be flagged. That exclusion is load-bearing, not an oversight, and is stated in the check.

**Two waivers, because a false positive must cost ten seconds.** Inline `locale-ok: <reason>` mirrors
`# noqa` / `# nosec`; the repo-level `.identifier-locale-allow` doubles as the migration debt ledger.
Every finding prints `path:line:token` plus the exact allowlist line to add.

**`metadata.category: process`.** `generate.sh` maps `git|process → workflow`, so the skill ships in
the existing `ai-skills-workflow` bundle. Inventing a category would cost a CI whitelist edit, a
`skills-authoring` delta, a `GROUP_DESC` entry and a new marketplace plugin, to ship the doctrine in
a bundle nobody enables.

**`bug-hunter` is deliberately not touched.** Its universal checklist covers behaviour under hostile
conditions, and every row names a defect a *test* would have caught. A naming item has no failing
test behind it, so adding one would violate *Checklists are scored against field defects* — the same
requirement that authorizes Q.5. The genuinely adversarial slice (a rename crossing a wire boundary
is a compatibility change and needs an old-name-client test) lives in
`references/migration.md` and links out to `bug-hunter` from there.

**No `UserPromptSubmit` hook.** The two existing hooks fire on prompt shape — a code-change request,
a caught guess. No prompt regex observes "the model is about to name a variable", and a hook that
fires on every technical prompt stops being read; `claude/global/hooks/verify-rite.py` records that
reasoning in its own header and warns that it would degrade the sibling reminder in the same array.
The trigger-free layer is `personal-rules.md`; the structural layer is CI.

**Q.5 is a regression gate, not remediation.** *Checklists are scored against field defects* requires
traceable provenance, and the provenance here is the maintainer's field report of 2026-08-14
(issue #76) — Portuguese identifiers and route paths shipped in target repos through this rite. The
honest caveat is recorded with it: the catalog's own examples are clean today, so Q.5 protects the
exemplar the model imitates rather than fixing an existing defect.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Prose-layer / machine-layer language boundary; the BR domain-term exception and its gate; the anti-corruption-layer naming rule; the new-code-only migration policy | `code-locale` | **new canonical home**; added to the `skills-authoring` canonical map |
| "Write the issue in the repository's working language" | `backlog` | already canonical (issue prose) — gains a prose-only clause + link, no rule changed |
| "Portuguese docs stay Portuguese" | `documentation` | already canonical (docs prose) — gains one carve-out line + link, no rule changed |
| "Subject line language follows the repo's existing convention" | `conventional-commit` | already canonical (commit prose) — gains one carve-out line + link, no rule changed |
| Issue headings may be in the repo's working language | `execute-backlog` | already canonical (rite instance) — gains the same scope clause |
| "A translation is an invention" / never improvise an unverified name | `verify-before-claiming` | already canonical — `code-locale` links to it as the general form and does not restate the ladder |
| Deviation bookkeeping when an unlisted term forces a stop-and-ask | `execute-backlog` | already canonical — rail 9 links out instead of restating the protocol |
| Adversarial testing of a rename that crosses a wire boundary | `bug-hunter` | already canonical — `references/migration.md` links to it; no methodology restated |
| Rollout-gated enforcement (log-then-enforce) as the shape of expand/contract | `python-rest-api` | already canonical — `references/migration.md` links to it rather than restating the mechanism |
| `snake_case → camelCase` zod parser as the JS anti-corruption layer | `react-api-client` | already canonical — `code-locale` cites it as the shipped instance |
| Format-level naming conventions (test method naming, DTO triple, `UPPER_SNAKE_CASE` codes, env prefixes) | the respective stack skills | already canonical — untouched; they govern *format*, this change governs *language* |

No mechanism list from a sibling skill is reproduced inline. Every entry marked "already canonical"
keeps its full text and receives at most one sentence plus a link.

## Risks / Trade-offs

- **A false positive blocks CI and the rule gets bypassed.** The dominant risk: a team that hits
  `--no-verify` once hits it forever. Mitigated by Tier 0 scope reduction, whole-segment matching,
  the 4-char floor, the `LEXICON ∩ ENGLISH_COLLISIONS == ∅` import assertion, two waivers with the
  exact allowlist line printed on every finding, and two mandatory false-positive proofs that must
  report zero findings before the check is wired
  (`skills/assettoserver-csp-lua/references/snippets.lua`, which carries accented text in comments
  and inside a UTF-8-escaped literal; and `skills/conventional-commit/SKILL.md:108-119`, an untagged
  Portuguese fence).
- **The domain-term exception swallows the rule.** Mitigated by requiring the Glossary row or an
  inline `locale-ok: <reason>`; an unlisted Portuguese noun is a defect, not a domain term.
- **A word list is not a language model.** Open vocabulary escapes, and so do Portuguese words that
  are also English words. Declared explicitly inside the check per *Partial coverage is declared,
  not implied*, rather than implied as full coverage. The lexicon grows only from real defects, each
  recorded with the identifier that earned it.
- **Doctrine misread as "everything English".** Mitigated by the name, by leading with the prose
  layer rather than the machine layer, and by adding carve-out lines to the three prose rules
  instead of editing them.
- **Cross-link inflation.** Nine `## See also` bullets, not thirty; `fivem-fallback`,
  `assettoserver-ops`, `assettoserver-csp-lua`, `helm-migration`, `observability`,
  `k8s-tune-resources` and the ten `r3f-*` skills get nothing and reach the rule through their
  siblings and `personal-rules.md`.
- **The detector's own claims going stale.** Every command it prescribes is probed on this machine
  and the versions and date are recorded, per *Versioned external APIs are pinned*.
- **`--diff` mode gives weaker coverage than a full-tree scan.** Accepted deliberately: whole-tree
  enforcement on a legacy repo produces a red pipeline on day one, which is how a rule dies. The
  trade is stated in `references/migration.md` rather than hidden.

## Open Questions

None outstanding. The two questions that would have been open were resolved by decision rather than
deferral: whether to enforce whole-tree or diff-only (diff-only, for the adoption reason above), and
whether the doctrine belongs in `shared/conventions/` (no — that directory is loaded by nothing;
recorded as a follow-up in `tasks.md` E.4, not resolved here).
