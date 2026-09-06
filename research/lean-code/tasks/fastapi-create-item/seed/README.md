# inventory

Small FastAPI service. Conventions:

- every response is the envelope in `app/schemas/common.py` (`success(...)`) or the error shape the
  handlers in `app/core/exceptions.py` produce — endpoints never return bare dicts or raise
  `HTTPException` themselves;
- response codes are registered in `app/core/response_codes.py` before use;
- the tenant is `X-Tenant-Id`, resolved by `app/api/dependencies.py`, and every repository call is scoped
  by it;
- tests live in `tests/` and use `fastapi.testclient`.

```
pip install -r requirements.txt
pytest
```
