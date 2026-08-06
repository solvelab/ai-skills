## 1. Measure before writing

- [x] 1.1 Probe the installed versions (`SQLAlchemy 2.0.51`, `pytest-asyncio 1.4.0`) and confirm
      `AsyncSession` / `create_async_engine` import
- [x] 1.2 Measure event-loop blocking: 10 concurrent 50 ms calls, blocking vs awaited
- [x] 1.3 Record the numbers and the conditions (501 ms vs 50 ms, 10x)

## 2. python-rest-api (1.4.0)

- [x] 2.1 Add **Async or sync — pick one lane per endpoint** above the DB section
- [x] 2.2 State the rule and the two coherent lanes; name the sync lane the default
- [x] 2.3 Name the middleware/handler trap explicitly
- [x] 2.4 Give the async lane's engine, sessionmaker, dependency and `asyncio_mode`
- [x] 2.5 Document the green-suite failure (sync override in an async fixture)
- [x] 2.6 Link `backend-resilience` for the outbound half
- [x] 2.7 Name the lane in the DB section's first bullet
- [x] 2.8 Pin the probed versions; update the description; bump to 1.4.0

## 3. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers unchanged; description gains the lane rule
- [x] Q.4 No duplicated doctrine: outbound half stays in `backend-resilience`, linked not restated
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 Description states no policy the body contradicts
- [x] Q.7 No README change — skill purpose unchanged

## 4. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-async-lane-rule --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync
- [x] V.4 `scripts/validate-skills.py` 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 12/12
- [ ] V.6 `openspec archive add-async-lane-rule --yes` after review
