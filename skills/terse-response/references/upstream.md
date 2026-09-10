# Provenance — where this skill comes from, and the plugin it replaces

## Upstream

| | |
|---|---|
| Project | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) |
| Licence of the harvested file | MIT (the upstream's `LICENSE` scope note keeps `skills/` under MIT; its engine directories are BSL-1.1 and nothing from them is used) |
| Version read | plugin 2.3.1, installed cache `~/.claude/plugins/cache/caveman/caveman/81536f57b330` |
| Commit | `81536f57b3303b7de7f5bc5b564cc344f9112d68` (`installed_plugins.json`, gitCommitSha) |
| File | the upstream's caveman skill file (https://github.com/JuliusBrussee/caveman/blob/81536f57b3303b7de7f5bc5b564cc344f9112d68/skills/caveman/SKILL.md), 6698 bytes, sha256 `3edd677596cbf12f010f25f05dfb1e8a6c9c178d92499c86e5b5afa44c86c16c` |
| Read on | 2026-09-10, issue #248 |

Copyright of the upstream text remains with its author; this skill is a rewrite in the catalog's
format with attribution, as the MIT licence allows.

## What entered, rewritten

- The compression rules of the `full` level: articles, filler, pleasantries, hedging, tool-call
  narration, decorative tables and emoji, raw error dumps, short synonyms, the
  `[thing] [action] [reason]. [next step].` pattern and its Not/Yes example.
- The "never drops" list: negations, numbers and units, technical terms, code, error strings, the
  user's language, standard acronyms, the tokenizer argument against invented abbreviations and
  arrows.
- "Never add a word to sound terse", the pronoun/copula and verb-form points, the "if not shorter,
  use plain" rule.
- Auto-clarity (security, irreversible action, misreadable sequence, technical ambiguity, a request
  to clarify) with the destructive-operation example.
- The boundaries: everything persisted outside the chat is normal prose.
- Persistence for the whole session and the stop phrase.

## What was left out, and why

| Left out | Why |
|---|---|
| Intensity levels `lite`, `ultra`, `wenyan-*` and their table and examples | The maintainer runs `full` only (`~/.claude/.caveman-active` -> `full`); six registers were 40 % of the upstream text for zero use. One register, edited if a different one is ever wanted. |
| `/caveman <level>` switching, `/caveman-*` commands (commit, review, compress, stats, help, init) | Commands are plugin mechanics; the catalog has `conventional-commit` and `documentation` for the persisted artifacts, and this skill leaves those alone by design. |
| `SessionStart` hook (`src/hooks/caveman-activate.js`), `UserPromptSubmit` tracker (`caveman-mode-tracker.js`), the `.caveman-active` flag file | The always-on path here is the maintainer's rules file, loaded by `@` into every session; no script runs. The tracker re-injected a one-line reminder per prompt and ran `caveman-stats` via `execFileSync`; the register survives long sessions by instruction instead. |
| `cavecrew-*` agents and `cavecrew-model-overrides.js` (rewrites agent files from env vars) | Not used, and exactly the kind of executable a third party should not run in the session. |
| `caveman-stats`, "Caveman Cloud" skills (`setup`, `discover`, `evidence-review`, `learn`, `manage`, `optimize`), the engine, MCP tools | Telemetry and product features; not part of a response register. |
| The "cuts output tokens 65 % (measured)" claim | This catalog publishes no effect number without its own measurement (`skills-catalog`: *A published cost claim carries re-runnable backing*). The measurement that exists for response shape on the maintainer's model is [research/i-have-adhd/results.md](https://github.com/solvelab/ai-skills/blob/master/research/i-have-adhd/results.md) (NO-CLAIM); this skill's only gate is non-regression against the upstream text, recorded there. |

## Removing the plugin (maintainer's machine, outside the catalog)

The catalog does not touch `~/.claude`. Once this skill is installed (plugin `ai-skills-workflow`)
and the *Terse Response* block is in the maintainer's rules file, the plugin can go:

```bash
claude plugin uninstall caveman@caveman
```

Then, by hand, in `~/.claude/settings.json`: remove `"caveman@caveman": true` from
`enabledPlugins` and the `caveman` entry from `extraKnownMarketplaces`; in
`~/.claude/settings.local.json`: remove the two `permissions.allow` entries that name
`~/.claude/hooks/caveman-config.js`; and delete the flag file `~/.claude/.caveman-active`.
A new session then shows no `CAVEMAN MODE ACTIVE` line from a hook and still answers terse,
because the rules file carries the block.
