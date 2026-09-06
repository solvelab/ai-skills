# Review lens on the published guard — `lens4/`, 2026-09-06

The three lens cells of item #174: one `claude -p` per diff on `opus[1m]`, Claude Code `2.1.261`
pinned, `--setting-sources project,local`, the `lean-code` skill copied from master `e7f5fe8`
(the published text, with the widened guard sentence of `6831e24`) into `.claude/skills/lean-code`
of a git-root cwd, `skillOverrides.lean-code = "on"`, the diff restricted to the one file the
protocol names. Line numbers are lines of the `diff.patch` the cell read. Finding lines and the
`net:` line only, verbatim; the adjudication by the five false-positive rules is in
[`../results.md`](../results.md).

## `49c44d0` (#140) — `claude/global/hooks/locale-rite.py` — $0.5362

```
L213: delete: `CONTEXT_LINE_CAP = 200` is defined and never read — `report()` truncates on `CONTEXT_CAP` alone. Drop the constant; the 200-line probe stays recorded in the comment above it.
L253-257: yagni: `current_mode()` is a one-line `os.environ.get` wrapper with a single caller. Inline `os.environ.get(MODE_ENV, "").strip().lower()` at L455.
L281-282: delete: the empty-anchor guard duplicates the fallback below — `body.find("")` returns 0, so the function already returns 1 for an empty anchor. Nothing.
L432: shrink: the `isinstance(file_path, str)` guard is already covered by the `except Exception: return None` at L448 — `Path(42)` raises inside `findings_for` and evaluate returns None either way. Back to `if not file_path:`.
L443-444: delete: same for the `isinstance(anchor, str)` guard — a non-str anchor raises in `body.find()`, inside the same try. Nothing.
net: -9 lines possible.
```

## `69aaf73` (#141) — `claude/global/hooks/locale-stop-gate.py` — $0.6960

```
L119-181,224-229,248-249: shrink: the diff-pin and never-silent-truncation rationales are each argued three times — the docstring WHY block, the constant's comment, then again under KNOWN LIMIT. Keep each argument once in the docstring, one-line pointer at the constant.
L183-191: delete: wiring JSON snippet duplicated in the README hooks section (commit body, L17). One line pointing at the README.
L234-237,323-326: yagni: two mechanisms for one empty-tree id — a `hash-object` subprocess plus the SHA-1 constant as its fallback. `base = "HEAD" if head[0] == 0 else EMPTY_TREE_SHA1`, marked `# lean: SHA-1 empty tree -> recompute when a SHA-256 repo shows up`.
L259-263,387-395: shrink: second-Stop copies of both messages (`UNMEASURED_MESSAGE`, `remaining_message` with a hand-rolled finding formatter that `f.render()` already produces, `:0` case included). One `SECOND_STOP` prefix constant on the existing block texts.
L307-308,353,408-419: yagni: `vendored=None` guard whose only caller always passes `lambda rel: check.is_vendored(rel)`, plus `environment` and `git_env` normalizing `env` twice. Required `vendored`, pass `check.is_vendored`, and `env = os.environ if env is None else env` once at the top.
net: -63 lines possible.
```

## `b1f527f` (#142) — `skills/code-locale/references/pre-commit-locale.sh` — $0.3346

```
L135, L199: yagni: `LOCALE_CHECK_SHA256=skip` escape and its header paragraph — a config nobody sets, next to two documented bypasses (`LOCALE_CHECK`, `--no-verify`). Drop the `skip` branch and the header line.
L202-208: shrink: four `log` calls for one digest mismatch. One line with expected/got, plus the existing "bump both (header: THE PIN)" pointer.
L219-220: shrink: two-element loop with a `case /"${CHECK_REL}") continue` sentinel to detect an unset `AI_SKILLS_HOME`. `for candidate in ${AI_SKILLS_HOME:+"$AI_SKILLS_HOME/$CHECK_REL"} "$HOME/ai-skills/$CHECK_REL"` — the guard line goes away.
L232: delete: `command -v curl` pre-flight. The `if ! curl -fsSL` branch three lines down already refuses with a message.
L246: delete: `command -v git` guard. Git is what executes a pre-commit hook.
L183-184, L254-256, L263: yagni: `EXTRA_ARGS=()` — an empty knob nobody sets, and it is the sole reason for the `${arr[@]+"${arr[@]}"}` bash-3.2 dance and its 2-line comment. Keep a plain `english_arg=""` set to `--no-english`, unquoted at the call.
L275-277: shrink: grepping the detector's own output for `advisory` to decide whether to echo it. On rc=0, `[ -n "$output" ] && printf '%s\n' "$output" >&2`.
net: -14 lines possible.
```

The third cell closed by naming two things it deliberately did **not** flag: the ~100-line header
(each block names a measured refusal it prevents) and the `rc` → `70` remap at L266-270 (the check
behind the gate's non-trivial branch) — the two findings the pre-widening run (`lens3/`) had made on
this diff and the adjudication had counted as false positives under rule 3.

Totals: 17 findings (delete 5, yagni 5, shrink 7; no `stdlib:`/`native:`), `net:` 3/3 present,
$1.5668 (0.536152 + 0.696019 + 0.334646, `total_cost_usd` of each `out.json`).
