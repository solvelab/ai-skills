# The simplification ledger

Every deliberate simplification that cuts a real corner is marked in the code with one comment that
names its ceiling and the trigger to revisit it (`../SKILL.md`, *Marking a deliberate
simplification*). The ledger collects those markers into one list, so a deferral cannot quietly
become permanent.

## Grammar

```text
<comment-prefix> lean: <ceiling> -> <upgrade trigger>
```

- `<comment-prefix>` is the language's line comment: `#` (Python, Bash, YAML), `//` (JavaScript,
  TypeScript, C#, Go), `--` (Lua, SQL). Add the prefix your stack uses to the grep below.
- `<ceiling>` is the limit you accepted: `global lock`, `O(n²) scan`, `unbounded dict`, `ints only`.
- `->` is the ASCII separator the ledger splits on; the upstream used a comma, which appears inside
  most ceilings and separates nothing.
- `<upgrade trigger>` is the observation that makes the ceiling wrong: `per-account locks if
  throughput matters`, `lru_cache(maxsize) when memory shows up in a profile`.

```python
_cache: dict[str, bytes] = {}  # lean: unbounded dict -> lru_cache(maxsize) when memory shows up in a profile
```

```lua
local seen = {}  -- lean: table grows per session -> clear on player drop when memory is measured
```

## Scan

```bash
grep -rnE '(#|//|--) ?lean: ' --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist .
```

Each hit is one ledger row. The comment prefix keeps prose that merely *mentions* the convention out
of the ledger; a code block inside documentation (this file, a skill, a test fixture that carries a
marker as a string) still matches and is removed by hand — the ledger lists debt in the code that
ships, not the convention's own examples.

## Row format

One row per marker, grouped by file:

```text
<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.
```

Pull the ceiling and the trigger straight from the comment — the text before `->` and the text
after it. Want an owner per row too? Add `git blame -L<line>,<line> <file>`.

## The `no-trigger` tag

A marker with no `->` names a ceiling and no trigger. Tag its row `no-trigger`: those are the ones
that silently rot, because nothing says when to come back. The fix is to edit the comment, not the
code — write the trigger, or admit there is none and delete the marker (a corner with no upgrade
path is a decision, not debt).

## Footer

End with `<N> markers, <M> with no trigger.` Nothing found: `No lean: debt. Clean ledger.`

The ledger reads and reports; it changes nothing. To persist it, write the rows to a file
(`LEAN-DEBT.md` or the project's debt log) in the same change that reviewed them.

## Coexistence with `locale-ok:`

The `code-locale` skill's inline waiver (`# locale-ok: <reason>`) covers its own line and the next
one, so it sits on the line **above** the name it justifies (`skills/code-locale/SKILL.md`,
*Reviewing a diff*, in the `code-locale` skill). The `lean:` marker trails the code line it
simplifies. One marker per comment: the two never share a line, and neither parser has to know about
the other.

```python
# locale-ok: SEFAZ fiscal document, no faithful English translation
nota_fiscal_cache: dict[str, bytes] = {}  # lean: unbounded dict -> lru_cache(maxsize) when memory shows up in a profile
```

Adapted from `ponytail/skills/ponytail-debt/SKILL.md` of DietrichGebert/ponytail v4.9.0 (MIT) — the
comma separator became `->`, the marker name became `lean:`, and the coexistence rule is this
catalog's; see `upstream.md`.
