# Track — Python / pytest

The cycle's mechanics in a pytest project. The doctrine (what earns a cycle, what makes the first
test legitimate, when the cycle does not apply) is in `SKILL.md`; this file is only how to run it
here. The project's testing **stack** — fixtures, the integration marker, the golden OpenAPI
snapshot, the fuzz gate — belongs to `python-rest-api` and is not repeated.

## Where the first test goes

Beside the project's existing tests, in the directory pytest is already configured to collect. Read
that from the project rather than assuming it:

```bash
grep -rn "testpaths\|pythonpath" pytest.ini setup.cfg pyproject.toml tox.ini 2>/dev/null
```

A project with `testpaths = tests` and `pythonpath = src` collects `tests/` and imports modules
from `src/` by their bare name. Put the new file there, named for the behaviour rather than for the
module: `tests/test_duration_rejects_bare_numbers.py` says what broke when it goes red in CI;
`tests/test_utils.py` does not.

## Running it red

The point of the red step is the **reason** for the failure, not the failure itself. Run only the
new file, and read the error:

```bash
pytest tests/test_duration_rejects_bare_numbers.py -q
```

| what you see | what it means |
|---|---|
| `AssertionError` / `Failed: DID NOT RAISE` | red for the right reason — the behaviour is missing |
| `NotImplementedError` from the function under test | also right, when the seed is a stub |
| `ModuleNotFoundError`, `ImportError`, `fixture ... not found` | red for the **wrong** reason: the test never reached the behaviour. Fix the wiring, then run again |
| `no tests ran` (exit code 5) | pytest collected nothing — a filename or a function name that does not match `test_*`. This is not a red test, it is no test |
| `passed` | the test does not exercise what was asked. See *What makes the first test legitimate* in `SKILL.md` |

Exit code 5 deserves the extra line because it reads as success in a shell that only checks for
non-zero on failure paths, and as a green suite in a CI step that greps for `failed`.

## Writing the assertion so the missing behaviour is what fails

For a value:

```python
def test_combined_units_sum_to_seconds():
    assert parse_duration("1h30m") == 5400
```

For a rejection — the case most often written vacuously. `pytest.raises` fails the test when
nothing is raised, which is exactly what is wanted while the behaviour is missing:

```python
import pytest


def test_a_bare_number_is_rejected():
    with pytest.raises(ValueError):
        parse_duration("90")
```

Never `assert result is not None` against a stub: a placeholder return satisfies it and the test
pins nothing.

## A bug report is two tests, not one

The report names a symptom. The correct behaviour is a separate question, and a patch written from
the report alone often silences the symptom while returning a plausible wrong answer.

```python
def test_the_reported_crash_no_longer_happens():
    with pytest.raises(ValueError):          # not ZeroDivisionError
        percent_change(0.0, 10.0)


def test_the_case_the_report_did_not_mention():
    assert percent_change(0.0, 0.0) == 0.0   # nothing changed, so this is not an error
```

## Green, then tidy

Run the one file until it passes, then the whole suite before refactoring:

```bash
pytest tests/test_duration_rejects_bare_numbers.py -q   # the new behaviour
pytest -q                                               # nothing else broke
```

The refactor step adds no behaviour. If a new assertion becomes necessary while tidying, it is a
new cycle, not part of this one.

## What this track does not cover

Breaking the finished change on purpose — forged input, partial failure, concurrency — is
`bug-hunter` and its own pytest track. The minimum a change owes when the cycle does not apply is
the floor in `lean-code`.
