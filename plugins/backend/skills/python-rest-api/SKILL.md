---
name: python-rest-api
description: >-
  Conventions for Python REST APIs (FastAPI + pydantic v2), distilled from real solvelab production
  services. Use when creating or reviewing a Python API service — project layout, response envelope
  with centralized response codes, exception-handler registry (input errors are never raw 500),
  Field-constraint validation, tenant-isolation lookups, session-per-request DB access,
  pydantic-settings config, two-tier health endpoints, and the testing stack (SQLite unit fixtures,
  testcontainers integration marker, adversarial test naming, OpenAPI golden snapshot, Schemathesis
  fuzz gate). Also machine-to-machine service auth (named token catalog), domain-state idempotency
  with partial unique indexes, JSONB dialect variants, and out-of-process ingestion workers (UDP).
  The baseline that api-resilience-testing and bug-hunter assume.
metadata:
  author: solvelab
  version: 1.2.0
  category: backend
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

# Python REST API conventions

Distilled from real production services (fabcost3d-backend-rest-api and siblings). Prescriptive: follow
these unless the project documents a deliberate exception.

## Stack

FastAPI, pydantic v2 + pydantic-settings, SQLModel/SQLAlchemy 2 + psycopg, structlog, httpx,
Python ≥ 3.12. Dev: pytest (+pytest-asyncio, pytest-cov), ruff, testcontainers[postgres], schemathesis.

## Layout — strict layering

```
app/
  api/{dependencies.py, v1/{router.py, endpoints/*.py}}   # routers + DI wiring
  core/{config.py, exceptions.py, response_codes.py, logging.py, security.py}
  db/session.py                                           # engine + get_session dependency
  models/         # ORM entities (SQLModel)
  repositories/   # data access — one class per aggregate, generic BaseRepository[Model]
  schemas/        # pydantic DTOs — one file per resource
  services/       # business logic between routers and repositories
  main.py
tests/{conftest.py, test_*.py, integration/, golden/}
```

Flow is always **router → service → repository → DB**. Routers never touch the session directly;
services never build HTTP responses. Requests/responses use DTO triples per resource:
`XCreate` (required fields), `XUpdate` (all-`Optional`, default `None` — partial update), `XData`
(response, `from_attributes = True`).

## Response envelope + centralized codes

One error shape, defined once (`schemas/error.py`) and rendered by the exception handlers:

```python
class ErrorResponse(BaseModel):
    status: str = "error"
    code: str            # machine-readable, from core/response_codes.py
    message: str
    path: str
    details: Any | None = None
```

- All codes — success and error — live in `core/response_codes.py::ResponseCodes` as string constants
  (`NOT_FOUND`, `VALIDATION_ERROR`, `PRINTER_CREATED`, domain codes like `FILAMENT_STOCK_INSUFFICIENT`).
- Success mirrors the envelope with `status="success"` + `data`.
- Attach the documented error contract router-wide:
  `app.include_router(api_router, prefix="/api/v1", responses=COMMON_ERROR_RESPONSES)`.
- Drop-in implementation (envelope + full handler stack): `references/fastapi-envelope.md`.

## Error handling — input errors are NEVER a raw 500

Register handlers in `main.py`; each maps a failure class to the envelope:

| Exception | Status | Why |
|---|---|---|
| `AppException` subclasses | its own | typed business errors raised by services |
| `RequestValidationError` | 422 | pydantic input rejection |
| `IntegrityError` (unique/FK/not-null) | 409 | driven by request data, not a server fault |
| `DataError`, `decimal.InvalidOperation`, `OverflowError` | 400 | bad numeric/literal input |
| `SQLAlchemyError` | 500 | genuine DB fault |
| catch-all `Exception` | 500 | message hidden unless `APP_ENV == "dev"` |

Services raise the typed hierarchy from `core/exceptions.py` (`NotFoundException` → 404,
`BadRequestException` → 400, `ConflictException` → 409, `ValidationException` → 422,
`UnauthorizedException` → 401, `ForbiddenException` → 403) — never `HTTPException` directly.

## Validation

Every numeric knob gets an explicit `Field` constraint and a described default:
`Field(default=None, ge=1, le=128)`, `Decimal = Field(default=Decimal("0"), ge=0)`,
`str = Field(..., max_length=255)`. Optional tuning fields default to `None` so downstream defaults
aren't silently overridden.

## Tenant isolation (BOLA/IDOR)

Repository lookups for user-owned resources always take the pair — `find_by_id_and_user(id, user_id)` —
and services raise `NotFoundException` (not `ForbiddenException`) when the resource belongs to someone
else, so existence is not leaked. Regression-tested in `tests/test_bola_guards.py`-style suites.

## DB & transactions

- `Session(engine)` per request via the `get_session` dependency; engine with `pool_pre_ping=True`,
  bounded pool (`pool_size`/`max_overflow`), `pool_recycle`.
- Atomicity by transaction scoping: validate → mutate → **one** `session.commit()` per request. No
  partial commits mid-operation.
- **Domain-state idempotency for "at most one open X" semantics** (one open session per player,
  one active loan per user): enforce it in the DATABASE with a partial unique index —
  `create_index(..., ["player_id", "session_id"], unique=True,
  postgresql_where=sa.text("disconnected_at IS NULL"))` — and make the create endpoint idempotent:
  return the existing open row if found; on a concurrent-race `IntegrityError`, `rollback()` and
  re-read the winner instead of failing:

  ```python
  try:
      self.repo.add(row); self.session.commit()
  except IntegrityError:
      self.session.rollback()
      existing = self.repo.get_open(payload.player_id, payload.session_id)
      if existing is not None:
          return existing
      raise
  ```

  The close endpoint is idempotent too (closing a closed row is a no-op). Header-nonce idempotency
  keys are for paid client mutations; domain-state idempotency is for presence/lifecycle facts.
- **Pessimistic mode for contended state** (money, stock, debts — anywhere a lost update costs
  something real): repositories expose `get_for_update()` / `for_update: bool` params
  (`SELECT ... FOR UPDATE` via `with_for_update()`), and `commit: bool = True` flags so callers can
  **stage** (`add`+`flush`) inside a larger atomic section. Compose with `session.begin_nested()`
  (SAVEPOINT) + locks + staged writes + one final `session.commit()`. Simple CRUD stays optimistic;
  reach for locks only where two concurrent writers can both "win".
  Known limit: `FOR UPDATE` is a no-op on SQLite — concurrency is only truly validated against
  Postgres; state that limit in the test.
- Migrations: services with real schema evolution use **Alembic** (`alembic upgrade head` at boot via
  the entrypoint). Small fixed-schema services may deliberately skip it (`create_tables()` + additive
  column sync at startup) — pick one mode explicitly, don't half-adopt.

## Config

`pydantic_settings.BaseSettings` with `SettingsConfigDict(env_file=".env", case_sensitive=False,
extra="ignore")`; env vars grouped by domain prefix (`APP_*`, `POSTGRES_*`, `JWT_*`, ...);
`database_url` as a `@computed_field` that normalizes the driver. Never scatter `os.environ.get` calls
through business code.

## API surface

- Versioned prefix (`/api/v1`) even at small scale.
- Two-tier health: `GET /health` (liveness, no dependencies) and `GET /api/v1/health` (detailed,
  includes DB connectivity).

## Testing

- `tests/conftest.py`: in-memory SQLite (`create_engine("sqlite://", poolclass=StaticPool,
  connect_args={"check_same_thread": False})`) injected via `app.dependency_overrides[get_session]`;
  fixtures build the object graph + `auth_headers` with a real token.
- **Autouse state-reset fixtures**: any module-level state (config caches, cooldown dicts, visitor
  maps) gets an autouse fixture that resets it between tests — otherwise test order starts mattering.
  Same for enforcement flags: an autouse fixture disables boundary auth by default so business-rule
  tests aren't masked by 401s (boundary tests re-enable it explicitly).
- Postgres-only column types need a SQLite shim in conftest:
  `@compiles(JSONB, "sqlite")` → render as `JSON` so models load in unit tests. Better: declare the
  variant at the model — `Column(JSON().with_variant(JSONB, "postgresql"))` — JSONB on Postgres,
  plain JSON on SQLite, no conftest magic.
- SQLite stores naive datetimes while Postgres returns aware ones — aggregation/window code that
  compares stored timestamps must normalize (`dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)`)
  or unit tests and production disagree on the same data.
- `integration` pytest marker: testcontainers + real Postgres, auto-skipped without Docker — catches
  dialect issues SQLite misses (UUID, NUMERIC precision, ALTER TABLE).
- Adversarial suites follow `bug-hunter`: `test_*_adversarial` / `test_bola_guards` /
  `test_input_error_handlers`, and each test docstring cites **how the bug was found** (skill/fuzzer)
  and why it matters.
- **OpenAPI golden snapshot**: `tests/golden/openapi_schema.json` diffed against `app.openapi()` with
  `info.version` normalized (release bumps must not churn the contract test); regenerate explicitly
  via `UPDATE_GOLDEN=1`.
- **Fuzz gate in CI**: Schemathesis against the live app (`--checks not_a_server_error`) — any 5xx
  fails the build before release/publish.

## Rollout-gated enforcement (log-then-enforce)

When adding a security boundary to a **live** API (service token, ownership checks), ship it behind an
enforcement flag that defaults to **log-but-allow**:

```python
def require_service_auth(x_city_token: str | None = Header(None)) -> None:
    ok = bool(token) and hmac.compare_digest(x_city_token or "", token)
    if not ok:
        logger.warning("service_auth_failed", enforced=settings.SERVICE_AUTH_ENFORCED)
        if settings.SERVICE_AUTH_ENFORCED:
            raise UnauthorizedException(...)
```

- One release for clients to start sending the credential; flip the flag when logs show zero misses.
- Health endpoints stay exempt (probes have no credentials).
- Same pattern for ownership: `assert_owns(owner_id, actor_id, enforced=settings.OWNERSHIP_ENFORCED)`,
  with the actor resolved **server-side** from the session (never from the payload).
- The flag is temporary: remove it (enforce unconditionally) once the rollout completes.

## Service-to-service auth — named token catalog

When the callers are machines (game servers, collectors, sibling services), not users:

- One header (e.g. `X-Service-Token`) checked by a dependency; tokens come from a **named catalog**
  env var — `API_TOKENS=collector:tok1,game-server:tok2` — parsed leniently (skip malformed
  entries with a warning), optionally plus a `legacy` single-token var during migration.
- Compare with `hmac.compare_digest` (constant-time); on success return a typed
  `AuthPrincipal(integration=name)` so handlers know WHO called.
- **Log only the integration name, never the token** — `logger.info("auth_ok", integration=...)`.
- `ensure_auth_configuration()` runs at app import/boot and **fails startup** when enforcement is
  on but no tokens are configured — a boot crash beats an API that silently accepts everything.
- The same catalog + `authenticate_token()` is transport-agnostic: reuse it for non-HTTP inputs
  (a `token` field inside a UDP JSON datagram) instead of inventing a second credential scheme.
- Pairs with rollout-gated enforcement above: `AUTH_ENFORCED=false` logs
  `auth_not_enforced` and allows, until logs show every caller sends a valid token.

## Out-of-process ingestion workers

High-volume or lossy inputs (UDP telemetry, queues) run as a **separate process**
(`python -m app.workers.udp_collector`), never inside the HTTP runtime — but share the SAME
service layer (`EventService.ingest_event`) so validation and persistence rules exist once.
Worker hardening rules:

- Gate datagram/message size before parsing (`len(data) > max_bytes` → reject).
- Authenticate with the shared token catalog (field in the payload for UDP).
- **The worker never crashes on bad input**: known errors log a warning and drop; the handler ends
  with `except Exception: # worker must not crash on bad datagrams` — one hostile packet must not
  take ingestion down. Crash-on-bad-input is acceptable for HTTP (the framework contains it), not
  for a datagram loop.

## Lint / format

Ruff: `target-version` matching the runtime, `line-length = 100`, `select = ["E","F","I","W"]`; every
`ignore` entry carries a one-line justification comment (e.g. `E711`/`E712` required by SQLAlchemy
`== None` filter idiom). `ruff check` + `ruff format --check` in CI.

## See also

- `api-resilience-testing` — the negative/fuzz/contract methodology this baseline is tested against.
- `bug-hunter` — per-change adversarial rite (`references/track-python-pytest.md` assumes this stack).
- `backend-resilience` — fallback/negative-cache doctrine for calls this service makes to others.
- `conventional-commit` — commit format used by these services' semantic-release pipelines.
- `react-api-client` — the frontend counterpart consuming this envelope/code registry.
- `log-event-collector` — the log-tailing sidecar pattern that feeds a generic event-sink endpoint
  in this kind of service.
