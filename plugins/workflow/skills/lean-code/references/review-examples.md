# Review and fix examples

The lens (`../SKILL.md`, *Reviewing a diff*) is one line per finding: location, tag, what to cut,
what replaces it. The ❌ line is the review comment that costs a paragraph and changes nothing; the
✅ line is the same finding in the form a reader can act on.

## The lens, one line per tag

❌ "This EmailValidator class might be more complex than necessary, have you
considered whether all these validation rules are needed at this stage?"

✅ `L12-38: stdlib: 27-line validator class. "@" in email, 1 line, real validation is the confirmation mail.`

✅ `L4: native: moment.js imported for one format call. Intl.DateTimeFormat, 0 deps.`

✅ `repo.py:L88: yagni: AbstractRepository with one implementation. Inline it until a second one exists.`

✅ `L52-71: delete: retry wrapper around an idempotent local call. Nothing replaces it.`

✅ `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`

Then the net: `net: -71 lines possible.` — or `Lean already. Ship.`

What the lens never tags: a guard at a trust boundary (`yagni:` on payload validation is a false
positive — the carve-outs decide), a `stdlib:` naming a function the pinned runtime does not ship,
and the one smoke test or `assert` self-check behind non-trivial logic (`delete:` on a test is a
false positive, always).

## Before / after — email validation

The upstream's recorded run for the prompt *"Write me a Python function that validates email
addresses."* (Claude Haiku 4.5, temperature 1; `examples/email-validation.md` of the upstream,
`upstream.md` names the pin). Without the doctrine, 75 lines of code across three functions
(regex, "advanced" with length and dot rules, and a third-party library), a test table and a
comparison table. With it:

```python
import re


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))
```

`→ skipped: RFC 5322 parser, DNS MX lookup, confirmation email. Add when you actually need to reject
user+tag@sub.domain.co.uk or catch typos; until then this catches the fat-finger cases.`

75 → 3 lines of code, same model, same prompt. The lens on the long version would read:

```text
L20-58: yagni: validate_email_advanced duplicates validate_email with four string rules nobody asked for. Delete; the regex already answers the question.
L62-75: delete: third function wrapping a library the project does not install. Nothing replaces it.
L14-27: shrink: eight-row test table printing booleans. One assert on a valid and an invalid address.
net: -60 lines possible.
```

## A marker and its ledger row

```python
def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)  # lean: re-read on every call -> cache with a mtime check when a profile shows this in the hot path
```

Ledger row, produced by the grep in `simplification-ledger.md`:

```text
settings.py:12, config re-read on every call. ceiling: re-read on every call. upgrade: cache with a mtime check when a profile shows this in the hot path.
```

A marker written as `# lean: re-read on every call, cache later` has no `->` and lands in the
ledger as a `no-trigger` row: "later" is not an observation.

## Root cause, not symptom

The bug report: *"`transfer()` lets an account go negative."* Both `transfer` and `withdraw` route
through one shared helper; the report names only `transfer`.

```python
balances: dict[str, int] = {}


def _debit(account: str, cents: int) -> None:
    if balances.get(account, 0) < cents:
        raise ValueError("insufficient funds")
    balances[account] = balances.get(account, 0) - cents


def _credit(account: str, cents: int) -> None:
    balances[account] = balances.get(account, 0) + cents


def transfer(src: str, dst: str, cents: int) -> None:
    _debit(src, cents)
    _credit(dst, cents)


def withdraw(account: str, cents: int) -> None:
    _debit(account, cents)
```

The one runnable check lives beside the module, in `test_bank.py`, never inside it:

```python
from bank import balances, transfer, withdraw


def test_second_debit_cannot_overdraw() -> None:
    balances["a"] = 100
    withdraw("a", 60)
    try:
        transfer("a", "b", 60)
    except ValueError:
        pass
    assert balances["a"] == 40, balances
```

The fix is the two-line guard inside `_debit`: one place, both callers. The symptom fix — a check at
the top of `transfer()` — is a smaller-looking diff that leaves `withdraw()` overdrawing, and it is
what the lens tags when it sees a guard duplicated per caller: `yagni:` on the second copy, `shrink:`
on the first, replacement "one guard in `_debit`". `test_bank.py` is the one runnable check the
carve-outs require; it is never flagged, and it stays outside `bank.py` so the product file is the
two-line guard and nothing else. An inline `assert`-based `__main__` block is for a single-file
script that nothing imports — this module has two importers, so the check does not live in it (the
harness counted such a block as product code: `reuse-slug` 9 → 19, `cache` 3 → 11 added lines).

What the catalog's own baseline wrote for this shape (`trace-transfer`, 3/3 cells) was a custom
`InsufficientFunds(Exception)` class with a docstring, a separate `_check_amount()` with `isinstance`
and negativity checks, and 26-28 added lines against these two. All three cells did fix `_debit` —
the root-cause rule held without the skill; the over-build is what the ladder is for.

Adapted from `ponytail/skills/ponytail-review/SKILL.md` and `examples/email-validation.md` of
DietrichGebert/ponytail v4.9.0 (MIT); the marker, ledger and root-cause code are this catalog's —
see `upstream.md`.
