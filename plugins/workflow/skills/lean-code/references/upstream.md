# Upstream provenance

This skill adapts the development doctrine of **DietrichGebert/ponytail**, read at:

- Repository: <https://github.com/DietrichGebert/ponytail>
- Version: `4.9.0` (`package.json` at the pinned commit)
- Commit: `974d940a1c5344210874150b98ff0d2c861fab6a` (2026-09-04)
- Files read: `ponytail/skills/ponytail/SKILL.md`, `ponytail/skills/ponytail-review/SKILL.md`,
  `ponytail/skills/ponytail-audit/SKILL.md`, `ponytail/skills/ponytail-debt/SKILL.md`, `docs/platform-native.md`,
  `examples/email-validation.md`, `benchmarks/results/2026-06-18-agentic.md`, `LICENSE`

The text below that is marked **verbatim** is copied from those files and is covered by the
upstream's licence, reproduced in full here because the notice must travel with the copied text.

## Licence of the copied text

```text
MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## What is verbatim, what was rewritten, what was dropped

A future edit to a **verbatim** block changes text whose wording the upstream measured; edit it
knowing that, and record the edit here.

| Upstream text | Here | Status |
|---|---|---|
| `ponytail/skills/ponytail/SKILL.md:22-24` — "You have seen every over-engineered codebase and been paged at 3am for one. The best code is the code never written." | `SKILL.md`, thesis | **verbatim** (the "lazy senior developer" opening sentence dropped — see *Rewritten*) |
| `:32-48` — the seven-rung ladder and the "runs *after* you understand the problem" paragraph | `SKILL.md`, *The ladder* | **verbatim** |
| `:50-54` — "Bug fix = root cause, not symptom… grep every caller… Fix it once, where all callers route through." | `SKILL.md`, *Bug fix = root cause, not symptom* | **verbatim** |
| `:58-61, 63` — the rules on abstractions, boilerplate, deletion, fewest files, edge-case correctness | `SKILL.md`, *Rules* | **verbatim** |
| `:62` — "Complex request? Ship the lazy version and question it in the same response…" | `SKILL.md`, *Rules*, fifth bullet | **rewritten**: defers to the Doing / Not doing / Assumptions block of `verify-before-claiming`; the catalog never ships less than was asked on its own authority |
| `:64` — the `ponytail:` marker rule | `SKILL.md`, *Rules*, last bullet | **rewritten**: marker renamed `lean:`, grammar `<ceiling> -> <upgrade trigger>` with an ASCII separator (the upstream's comma appears inside ceilings) |
| `:66-75` — Output: "Code first… `[code] → skipped: [X], add when [Y].`" | `SKILL.md`, *What the delivery looks like* | **rewritten**: the pattern, "If the explanation is longer than the code, delete the explanation, every paragraph defending a simplification is complexity smuggled back in as prose" and "Explanation the user explicitly asked for… is not debt" are verbatim; "at most three short lines" dropped because `verify-before-claiming` requires inline sources; the trailer made mandatory |
| `:92-95` — "Never simplify away: input validation at trust boundaries…" | `SKILL.md`, *Never simplified away*, first paragraph | **verbatim** |
| `:97-101` — "Never lazy about understanding the problem…" | same section, third paragraph | **verbatim** |
| `:103-105` — "Hardware is never the ideal on paper… a PCA9685 runs a few percent fast…" | same section, fourth paragraph | **rewritten**: generalised to "a constant that models the physical world stays a knob"; PCA9685 became "a servo driver" |
| `:107-112` — "Lazy code without its check is unfinished…" | same section, last paragraph | **verbatim**, plus one sentence linking `bug-hunter` for what lies beyond one check |
| `ponytail/skills/ponytail-review/SKILL.md:13-27, 31-34, 46-48, 52-56` — the lens: format, five tags, the ❌/✅ pair, `net:`, `Lean already. Ship.`, the scope guard | `SKILL.md`, *Reviewing a diff*; `review-examples.md` | **verbatim** ("the ponytail minimum" → "the minimum") |
| `ponytail/skills/ponytail-review/SKILL.md:36-42` — the four other ✅ lines | `review-examples.md` | **verbatim** |
| `ponytail/skills/ponytail-audit/SKILL.md` — *Hunt* and *Output* | `SKILL.md`, *Reviewing a diff*, the *Repo-wide* paragraph | **rewritten** into one paragraph |
| `ponytail/skills/ponytail-debt/SKILL.md` — scan, row format, `no-trigger`, footer | `simplification-ledger.md` | **rewritten**: `->` separator, `lean:` name, coexistence rule with `locale-ok:` added |
| `docs/platform-native.md` | `platform-native.md` | **trimmed**: Swift/SwiftUI section dropped; every version qualifier ("Python 3.9+", "since 3.4") removed; the debounce comment rewritten to the `lean:` grammar; the header note on lookup vs support matrix is this catalog's |
| `examples/email-validation.md` — the 3-line "with" version and its skipped line | `review-examples.md` | **verbatim** code; the prose around it is this catalog's |
| Persona ("You are a lazy senior developer. Lazy means efficient, not careless."), *Persistence*, *Intensity* (lite/full/ultra), *Boundaries* ("stop ponytail"), `ponytail-gain`, `ponytail-help`, flags, statusline, hooks, MCP server, the 24 host adapters, benchmarks, marketing | — | **dropped**: "lazy" collides with the catalog's "best long-term outcome over speed"; the rest is distribution |

## Provenance of each adopted rule

Rule text that names its origin, as the catalog requires of every checklist row.

| Rule (as it stands in `SKILL.md`) | Provenance |
|---|---|
| The seven-rung ladder, verbatim | upstream doctrine; the upstream's agentic benchmark (`benchmarks/results/2026-06-18-agentic.md`) measured the literal text at −54 % LOC against −33 % for the paraphrase "Follow YAGNI principles, and prefer one-liner solutions" — aggregate measurement, the wording carries the effect |
| "runs *after* you understand the problem, not instead of it" | upstream doctrine, added after the upstream's own field reports of confident wrong fixes; aggregate measurement only |
| Bug fix = root cause: grep every caller, one guard in the shared function | upstream, the one rule with an isolated measurement: on the `trace-transfer` task the operational wording scored 6/6 root-cause fixes against 0/3 for the generic "fix the bug" prose (upstream benchmark notes at the pinned commit) |
| No unrequested abstractions; no scaffolding "for later"; deletion over addition; fewest files | upstream doctrine, aggregate measurement only; on this catalog the baseline shows the defect they target: a custom exception class for a guard 6/27, a `_check_amount()` nobody asked for 3/27, three helpers for a ten-line loop 4/27 ([`results/20260905-211512-baseline-defects.md`](https://github.com/solvelab/ai-skills/blob/master/research/lean-code/results/20260905-211512-baseline-defects.md)) |
| Complex request → a line in *Assumptions*, never a silent smaller version | this catalog: `verify-before-claiming`, *Off-script guard* (issue #76 field report — work nobody asked for shipped through the rite) |
| Two stdlib options, same size → the one correct on edge cases | upstream doctrine, aggregate measurement only |
| `lean:` marker with ceiling and trigger; `no-trigger` rows | upstream doctrine (`ponytail:` marker, `ponytail-debt`); the `->` grammar is this catalog's, decided in the plan for issue #146 because the ledger has to split the comment |
| Trailer `[code] → skipped: [X], add when [Y]`, mandatory | upstream output contract; the baseline's `output_contract` flag was 0/27 without the doctrine, so the trailer is what the skill arm is measured on |
| No hard line cap on the trailer | this catalog: `verify-before-claiming` requires inline sources; a cap would fight it |
| Never simplify away: trust boundary, data loss, security, accessibility, explicit request | upstream doctrine; the upstream's safety scoring held 20/20 with the literal carve-outs and lost a path-traversal guard (19/20) with the paraphrase; an external benchmark cited in the upstream's issue tracker found the doctrine "trims everyday bad-input handling on 5/24 tasks" — which is why the section is at the top with links |
| A constant that models the physical world stays a knob | upstream doctrine (hardware calibration), generalised here; aggregate measurement only |
| One runnable check behind non-trivial logic; YAGNI applies to tests too | upstream doctrine; on this catalog the baseline's `no_check` was 3/27, all on the structural React task whose seed has no test runner |
| Review lens: five tags, one line per finding, `net:`, never flag the smoke test | upstream doctrine (`ponytail-review`); the false-positive rules the catalog scores it with are in [`protocol.md`](https://github.com/solvelab/ai-skills/blob/master/research/lean-code/protocol.md) (written before the lens ran) |
| The lens runs before `/simplify` and `/code-review` | this catalog: the two built-ins are named in the description's anti-trigger clause so the skill does not compete with them |

## The upstream's numbers, with their conditions

Measured **by the upstream, on the upstream's harness**, at `benchmarks/results/2026-06-18-agentic.md`
of the pinned commit: Claude Code `2.1.177` headless, `claude-haiku-4-5-20251001`, `n=4`, LOC counted
by `git diff` on seeded repositories:

- **−54 % LOC, −22 % tokens, 20/20 safe** for the literal doctrine against the no-skill baseline;
- a caveman-style control: −20 % LOC and +7 % tokens;
- the paraphrase "Follow YAGNI, prefer one-liners": −33 % LOC and 19/20 safe (lost the path-traversal
  guard on `safe-path`);
- the upstream recorded a contamination bug in its own earlier run (the plugin's `SessionStart` hook
  fired on every arm, so the baseline was running the skill) and marked that result SUPERSEDED; it
  also declared its single-shot chat-LOC numbers (80–94 %) inflated and retracted that metric.

None of these numbers is a claim about this skill on this catalog. They were measured on another
model, another CLI version and another set of tasks. **Measured on this catalog: see
[`research/lean-code/results.md`](https://github.com/solvelab/ai-skills/blob/master/research/lean-code/results.md)**
— the baseline (`claude-opus-5[1m]`, Claude Code `2.1.261`, `n=3`, 27 cells) is there; the skill arm
is written there when it runs, and nowhere before.
