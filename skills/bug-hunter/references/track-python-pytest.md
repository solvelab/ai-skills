# Track — Backend REST (Python/pytest example stack)

The commands assume pytest + an HTTP test client (FastAPI `TestClient`, httpx) because that is the
reference stack; translate the assertions to your framework — the scenarios are what matter.

Run the E2E suite **before** any manual validation. Mirror existing `test_*_adversarial` /
`test_*_bughunt` / `test_*_atomicity` files when the project has them.

## Scenarios

- **Anti-forge / clamps**: out-of-range values clamped or rejected; payload carrying another owner's id
  → 403; implausible values discarded; numeric overflow (e.g. BIGINT) handled.
- **Atomicity**: monkeypatch the last step of the operation to raise → assert nothing committed
  (balance/state unchanged), then the retry succeeds and applies exactly once.
- **Dependency resilience**: mock the config/KV client to raise (timeout/connect error) → assert the
  fallback path and the negative cache (one attempt per fail-TTL); assert a real 404 is NOT
  negative-cached. (Definitions in `backend-resilience`.)
- **Concurrency**: fire N concurrent requests (100+, not two) on the same row/target and count how
  many reached the dependency — a single-flight or lock guard is invisible at two callers.
  Two concurrent requests on the same row/target remain the minimum case. Note the fixture limit: SQLite test
  fixtures don't enforce row locks — `SELECT ... FOR UPDATE` serialization is only truly validated
  against the real database (e.g. Postgres). State this limit in the test docstring.
- **Rate-limit / reconnect persistence** where the change touches them.

## Generating cases (property-based)

Probed on 2026-09-07 with `hypothesis 6.167.1` on Python 3.14. It earns its place on the pure
functions under the endpoint — the parser, the clamp, the key builder — never on the handler:

```python
from hypothesis import given, settings, strategies as st

@given(line=st.text(max_size=120))
@settings(max_examples=3000, deadline=None)
def test_tokenizer_never_invents_characters(line):
    code, _state, _fragments = split_prose(line, "python", None)
    assert set(code) <= set(line) | {" "}
```

Whatever it fails on is frozen as a plain `test_*` case carrying the literal input. The seed is not
the record.

## Scoring the suite (mutation)

Probed on 2026-09-07 with `cosmic-ray 8.7.0`. Scope the session to the module the change touched and
drive it with the suite that already covers that module:

```toml
# cr.toml
[cosmic-ray]
module-path = "path/to/changed_module.py"
timeout = 60.0
test-command = "python3 -m pytest tests/test_changed_module.py -x -q"

[cosmic-ray.distributor]
name = "local"
```

```bash
cosmic-ray init cr.toml session.sqlite    # enumerate the mutants
cosmic-ray exec cr.toml session.sqlite    # run the suite once per mutant
cr-report session.sqlite                  # killed / survived
```

**The wrong command is the one a reader reaches for first**: `mutmut run` on its defaults. `mutmut
3.7.0` guesses the source paths and assumes a `pytest` runner, so in a repository that declares
neither it stops before mutating anything — `FileNotFoundError: Could not figure out where the code
to mutate is. Please specify it by adding "source_paths=code_dir" in setup.cfg`. The second wrong
command is either tool aimed at the repository root: correct, and hours long, to answer a question
about one changed file.

Read the survivors by class rather than as a percentage. A `|` inside a type annotation has no
runtime effect and is noise; a survivor on a limit constant or on a comparison operator is the
Boundaries item of the universal checklist reporting that it was named and never tested.

## Exit criteria

Every scenario above that applies to the change exists as a pytest test and is green, or is explicitly
marked not-applicable with a reason.
