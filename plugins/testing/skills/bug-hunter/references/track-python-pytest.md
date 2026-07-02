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
- **Concurrency**: two concurrent requests on the same row/target. Note the fixture limit: SQLite test
  fixtures don't enforce row locks — `SELECT ... FOR UPDATE` serialization is only truly validated
  against the real database (e.g. Postgres). State this limit in the test docstring.
- **Rate-limit / reconnect persistence** where the change touches them.

## Exit criteria

Every scenario above that applies to the change exists as a pytest test and is green, or is explicitly
marked not-applicable with a reason.
