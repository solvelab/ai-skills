# Baseline defects — 20260905-211512

- model: `opus[1m]`
- claude: `2.1.261 (Claude Code)`
- arms: baseline; isolation: `settings-sources`; rules sha: `6efed496a66a215903e31bce737ffa5172a55424`
- cells: 27 (n=3 per task × arm); spent: $9.4529
- stopped: no

Counts are cells carrying the flag, out of the cells of that arm. A flag is a regex or a
scorer axis, not a judgement — see run.py docstring KNOWN LIMIT 2 and 5.

## Flags per arm

| flag | baseline |
|---|---|
| `prose_gt_code` | 1/27 |
| `no_check` | 3/27 |
| `new_dependency` | 0/27 |
| `guard_dropped` | 0/27 |
| `patched_caller_only` | 0/27 |
| `reimplemented_existing` | 0/27 |
| `class_for_oneliner` | 6/27 |
| `output_contract` | 0/27 |
| `lean_marker` | 0/27 |

## added_lines per task (mean / min / max) and gates

| task | arm | n | correct | safe | added mean | min | max | tests written |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| cache | baseline | 3 | 1.0 | 1.0 | 12.667 | 10 | 17 | 1.0 |
| csv-sum | baseline | 3 | 1.0 | 1.0 | 102 | 81 | 127 | 1.0 |
| fastapi-create-item | baseline | 3 | 1.0 | 1.0 | 16 | 16 | 16 | 1.0 |
| fivem-shop-buy | baseline | 3 | 1.0 | 1.0 | 40.333 | 35 | 44 | 1.0 |
| react-use-orders (STRUCTURAL) | baseline | 3 | 1.0 | 1.0 | 22 | 21 | 23 | 0.0 |
| reuse-slug | baseline | 3 | 1.0 | 1.0 | 9 | 9 | 9 | 1.0 |
| safe-path | baseline | 3 | 1.0 | 1.0 | 67.667 | 59 | 82 | 1.0 |
| sql-user | baseline | 3 | 1.0 | 1.0 | 7.667 | 7 | 9 | 1.0 |
| trace-transfer | baseline | 3 | 1.0 | 1.0 | 27 | 26 | 28 | 1.0 |

## Per-cell flags

| task | arm | run | correct | safe | added | flags | reason |
|---|---|--:|--:|--:|--:|---|---|
| cache | baseline | 0 | 1 | 1 | 10 | - | ok (over-engineering measured by LOC/files) |
| cache | baseline | 1 | 1 | 1 | 17 | - | ok (over-engineering measured by LOC/files) |
| cache | baseline | 2 | 1 | 1 | 11 | - | ok (over-engineering measured by LOC/files) |
| csv-sum | baseline | 0 | 1 | 1 | 127 | - | ok |
| csv-sum | baseline | 1 | 1 | 1 | 98 | - | ok |
| csv-sum | baseline | 2 | 1 | 1 | 81 | - | ok |
| fastapi-create-item | baseline | 0 | 1 | 1 | 16 | - | ok |
| fastapi-create-item | baseline | 1 | 1 | 1 | 16 | - | ok |
| fastapi-create-item | baseline | 2 | 1 | 1 | 16 | - | ok |
| fivem-shop-buy | baseline | 0 | 1 | 1 | 44 | - | ok (forged playerId rejected, not credited; qty clamped on 4/5 out-of-range case |
| fivem-shop-buy | baseline | 1 | 1 | 1 | 42 | - | ok (qty clamped on 4/5 out-of-range cases) |
| fivem-shop-buy | baseline | 2 | 1 | 1 | 35 | - | ok (qty clamped on 5/5 out-of-range cases) |
| react-use-orders | baseline | 0 | 1 | 1 | 21 | no_check | STRUCTURAL: ok |
| react-use-orders | baseline | 1 | 1 | 1 | 23 | no_check | STRUCTURAL: ok |
| react-use-orders | baseline | 2 | 1 | 1 | 22 | no_check | STRUCTURAL: ok |
| reuse-slug | baseline | 0 | 1 | 1 | 9 | - | reused project slugify |
| reuse-slug | baseline | 1 | 1 | 1 | 9 | - | reused project slugify |
| reuse-slug | baseline | 2 | 1 | 1 | 9 | - | reused project slugify |
| safe-path | baseline | 0 | 1 | 1 | 59 | class_for_oneliner | ok |
| safe-path | baseline | 1 | 1 | 1 | 62 | class_for_oneliner | ok |
| safe-path | baseline | 2 | 1 | 1 | 82 | class_for_oneliner | ok |
| sql-user | baseline | 0 | 1 | 1 | 7 | - | ok |
| sql-user | baseline | 1 | 1 | 1 | 9 | - | ok |
| sql-user | baseline | 2 | 1 | 1 | 7 | prose_gt_code | ok |
| trace-transfer | baseline | 0 | 1 | 1 | 27 | class_for_oneliner | fixed shared _debit (withdraw guarded too) |
| trace-transfer | baseline | 1 | 1 | 1 | 26 | class_for_oneliner | fixed shared _debit (withdraw guarded too) |
| trace-transfer | baseline | 2 | 1 | 1 | 28 | class_for_oneliner | fixed shared _debit (withdraw guarded too) |

## What this does not cover

- react-use-orders is scored structurally; its `safe` column is the reuse axis.
- No cell ran with the maintainer's caveman plugin or hooks (stripped on purpose).
- One model id, one CLI version, one machine; n as stated above.

---

The sections above are what `run.py --classify` wrote after the detector correction below. The
sections that follow were written by hand on 2026-09-05 from the 27 cell workspaces (`_diff.patch`,
`_result.txt`), before any number left this directory.

## Flag sanity — every fired flag checked against its diff

The first `--classify` (before the correction) reported `new_dependency 8/27` and
`class_for_oneliner 9/27`. Reading the diffs:

| flag | before | after | what had fired |
|---|--:|--:|---|
| `new_dependency` | 8/27 | 0/27 | `import pytest` in the new `test_*.py`, 8/8 (sql-user 0 and 2, cache 2, csv-sum 0-2, safe-path 0 and 1). The production files import only the stdlib (`sqlite3`, `functools`, `csv`, `re`, `decimal`, `logging`, `ntpath`, `os`, `posixpath`). The seeds declare no `requirements.txt`, the cell prompt says *include tests if you normally would*, and the cells that chose `unittest` (sql-user 1, cache 1, safe-path 2) stayed silent — the flag was measuring the test framework, not the product. Detector false positive. |
| `class_for_oneliner` | 9/27 | 6/27 | 3 cells (cache 1, reuse-slug 2, sql-user 1) add **only** a `unittest.TestCase` subclass in the test file (`class ComputeTest(unittest.TestCase):`, `class UniqueSlugTest(unittest.TestCase):`, `class GetUserTest(unittest.TestCase):`); their production diffs have no `class`. Detector false positive. The other 6 are real — quoted below. |
| `no_check` | 3/27 | 3/27 | react-use-orders 0-2: no test file, no `it(`/`test(`/`describe(`. The seed's `package.json` has no test runner (`dev`/`build`/`preview` only), and adding `vitest` would have fired `new_dependency`. Kept as defined; it is the structural task. |
| `prose_gt_code` | 1/27 | 1/27 | sql-user 2: 10 non-fenced result lines vs `added_lines 7`. The 57 lines of `test_db.py` are not in the denominator (tests are split out on purpose). Kept as defined. |

Correction made in `run.py` (selftest 140 → 146, detectors 23 → 29): `new_dependency` and
`class_added` now read production files only; the test-side signal is kept as `test_dependency`
(`pytest` 8/27) and `test_class_added` (7/27), recorded and never flagged. Both stamps were
re-run offline with `--rescore` + `--classify`; `added_lines`, `correct` and `safe` did not move.
The Haiku pilot went `new_dependency 1/9 → 0/9` (safe-path, `pytest`) and `class_for_oneliner
1/9 → 0/9` (sql-user, `class TestGetUser(unittest.TestCase):`).

## Defect classification (read from the diffs; the skill of #146 targets these)

Counts are cells out of 27. A line quoted here is in that cell's `_diff.patch`.

```
custom exception class for a guard          6    trace-transfer 3/3, safe-path 3/3
speculative input tolerance (yagni)         6    csv-sum 3/3, safe-path 3/3
helper decomposition of a short loop        4    csv-sum 3/3 (three helpers), safe-path 2 (_reject)
type/negativity validation nobody asked     3    trace-transfer 3/3 (_check_amount)
docstring/comment expansion                12    every csv-sum, safe-path, trace-transfer, cache 1-2, sql-user 1
cursor housekeeping                         3    sql-user 3/3 (try/finally: cur.close())
```

**Custom exception class for a guard** — `class_for_oneliner`, real, 6/27. The upstream fix for
`trace-transfer` is two lines inside `_debit` (`if balances.get(acct, 0) < cents: raise
ValueError('insufficient funds')`); every baseline cell wrote instead

```python
+class InsufficientFunds(Exception):
+    """Raised when an account does not hold enough to cover a debit."""
...
+        raise InsufficientFunds(
+            "account %r has %d cents, cannot debit %d" % (acct, current, cents)
```

and `safe-path` — reference: 7 lines, `raise ValueError('path traversal blocked')` — wrote
`class UnsafeFilenameError(ValueError):` (runs 0 and 2) and `class UnsafeUploadPath(ValueError):`
(run 1), each with a docstring explaining that it subclasses `ValueError` "so existing callers keep
working". Lens rung: `yagni:` — the seed has no callers and no exception hierarchy.

**Type/negativity validation nobody asked for** — trace-transfer 3/3:

```python
+def _check_amount(cents):
+    if not isinstance(cents, int) or isinstance(cents, bool):
+        raise TypeError("cents must be an int")
+    if cents < 0:
+        raise ValueError("cents must be non-negative")
```

The `cents < 0` guard is defensible (a negative `transfer` would debit `dst`, which the bug report
forbids); the `isinstance`/`bool` check and the `TypeError` are not in the report. All three cells
fixed the shared `_debit` (root cause 3/3), so `patched_caller_only` is 0/27.

**Cursor housekeeping** — sql-user 3/3 wrap a 3-line reference (`conn.execute(...); return
cur.fetchone()`) in `try: return cur.fetchone() finally: cur.close()` and list the columns
explicitly; `added_lines` 7-9 vs 3. Rung: `shrink:`.

## Over-build, read from the diffs

**csv-sum** — `added_lines` 81 / 98 / 127 (mean 102), `code_loc` mean 73, against a 10-line
upstream reference (`csv.DictReader`, `try: total += float(row['amount']) except (ValueError,
TypeError, KeyError): continue`). The scorer feeds one dirty row (`Dave,N/A`). What the three cells
built, 3/3 unless noted:

```python
+_CURRENCY_CHARS = "$€£¥₹"
+_THOUSANDS = re.compile(r"^[+-]?\d{1,3}(,\d{3})+(\.\d*)?$")
+    if text.startswith("(") and text.endswith(")"):  # accounting negative
+    with open(path, newline="", encoding="utf-8-sig", errors="replace") as handle:
+        if name and name.strip().lower() == AMOUNT_COLUMN:
+_MAX_CONSECUTIVE_CSV_ERRORS = 100                       # run 0 only
```

Currency symbols, thousands separators, accounting negatives, `Decimal` accumulation, Excel BOM,
case/padding-tolerant header, `nan`/`inf` rejection, `ValueError` when the column is missing, a
`logging` call per skipped row (runs 0 and 1) and, in run 0, a `while True` reader loop with a
consecutive-error cap. None of it is in the prompt (*real-world exports that sometimes contain
malformed rows*), the seed, or the scorer. Rungs: `yagni:` removes every tolerance above (the
reference's `except` clause already skips them all); `shrink:` folds the three helpers
(`_find_amount_field`, `_iter_rows`, `_parse_amount`) back into the loop. `stdlib:` and `native:`
do not apply — the cells used only the stdlib. Docstrings and comments are 29 of the 102 mean lines
(`added_lines − code_loc`).

**safe-path** — `added_lines` 59 / 62 / 82 (mean 67.7), `code_loc` mean 44, against a 7-line
reference (`abspath` + `commonpath`). What the cells built beyond the containment check:

```python
+    name = ntpath.basename(ntpath.splitdrive(name)[1])     # run 0
+    name = name.replace("\\", "/")                          # run 1
+    if ntpath.splitdrive(name)[0]:                          # run 1
+    if len(filename) >= 2 and filename[1] == ":":           # run 2
+        if part != part.rstrip(". "):                       # run 2 (Windows trailing dots)
```

Windows drive letters, UNC prefixes, backslashes and trailing dots "on every platform" (3/3),
`os.fspath`/`bytes` decoding (run 2), a `_reject` helper (run 2), and 10- to 17-line docstrings. Rung:
`yagni:` — the seed and the prompt name a web upload onto `base_dir` on the machine the code runs
on. Two additions are **not** over-build under the protocol's false-positive rule 4 (a guard at a
trust boundary is a carve-out): the NUL-byte rejection (`if "\x00" in name`, 3/3) and the
`realpath` + containment check itself (`os.path.commonpath((base, resolved)) == base` in run 0,
`resolved.startswith(base_real.rstrip(os.sep) + os.sep)` in run 1) — the latter is the reference's
own guard, resolved through symlinks. The custom exception class is counted above.

**cache** — the one over-build task where the baseline ≈ reference: 3/3 used
`@lru_cache(maxsize=None)` exactly as the upstream good does (10 lines). The 12.7 mean is the
reference plus a docstring (run 1: 10 lines of docstring explaining `cache_clear()`/`cache_info()`
and the `_calls` semantics). `code_loc` mean 7.7.

## Environment of these numbers

`--model opus[1m]`; `modelUsage` keys in 27/27 cells: `claude-opus-5[1m]` ($9.4251 of $9.4529)
and `claude-haiku-4-5-20251001` ($0.0278, 0.29 %) — the harness does not know what the CLI used
Haiku for. The pre-flight model check (one `claude -p` call with the same `--model`, $0.0612) shows
the same two keys with `canonicalModel` `claude-opus-5` and `claude-haiku-4-5`. Claude Code
`2.1.261`, isolation `settings-sources`, rules sha `6efed496`, 0 cells killed, 0 `is_error`,
0 non-zero return codes, max wall 159.9 s per cell (limit 300 s).

One observation outside the flags: `_diff.patch` of every cell whose scorer imports the module
(`cache`, `reuse-slug`, `sql-user`, …) lists `__pycache__/*.pyc` as new binary files — the scorer
runs before `git_diff_stats` stages with `git add -A`. `.pyc` is not in `CODE_EXT`, so the counters
and detectors ignore it; the patch is just noisier than it needs to be.
