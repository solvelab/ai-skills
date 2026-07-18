# Validation discovery — run what exists, never invent

Order of authority for discovering a repo's checks:

1. **Repo docs**: README/CONTRIBUTING/CLAUDE.md "how to test/build" sections.
2. **CI workflows**: `.github/workflows/*.yml` — the steps CI runs are the ground truth.
3. **Manifests** (fallback):

| Signal | Likely commands |
|---|---|
| `package.json` scripts | `npm test`, `npm run lint`, `npm run build`, `npm run typecheck` (only scripts that exist) |
| `pyproject.toml` / `pytest.ini` / `tests/` | `pytest -q`; `ruff check` if configured |
| `Makefile` | documented targets (`make test`, `make lint`) |
| `go.mod` | `go test ./...`, `go vet ./...` |
| `Cargo.toml` | `cargo test`, `cargo clippy` |
| `*.csproj` / `*.sln` | `dotnet build`, `dotnet test` |
| `.busted` / `*_spec.lua` | `busted` |
| `fxmanifest.lua` (FiveM) | usually no runnable suite — validate pure-Lua modules with busted if present; otherwise state that runtime validation requires the server |

Rules:

- Run only commands the repo itself declares. Nothing discovered → say so explicitly in the
  report; do not silently skip.
- Never run: migrations, deploys, `docker compose up` against shared infra, or anything mutating
  external state — unless the user explicitly asks.
- Failures: fix and re-run. Unfixable within scope → report the exact output and stop for
  direction; never present a red check as green.
- Record each command + outcome (pass/fail/skipped-not-present) for the final evidence summary.
