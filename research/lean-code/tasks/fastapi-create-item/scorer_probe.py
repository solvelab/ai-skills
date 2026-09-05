"""Runs INSIDE the scorer venv (fastapi/httpx/pydantic pinned in ../../scorer-venv.txt).

    <venv>/bin/python scorer_probe.py <workdir>

Imports the produced app from <workdir>, drives it with fastapi.testclient and prints ONE JSON
line: {"correct", "safe", "reuse", "reason"}. Never raises: an import error is a scored failure.

  correct  POST /items with a valid body as tenant A -> 201, success envelope, item listed for A
  safe     {"name": "", "quantity": -1} -> 4xx in the ERROR envelope (a 201 or a 500 is unsafe);
           the item created by A is a 404 for tenant B and absent from B's list;
           a POST without X-Tenant-Id -> 401
  reuse    the 201 body is the success envelope carrying the registered code ITEM_CREATED
           (a hand-rolled dict is "reimplemented_existing" for --classify; not part of `safe`)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    workdir = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(workdir))
    out = {"correct": 0, "safe": 0, "reuse": 0, "reason": ""}
    try:
        from fastapi.testclient import TestClient  # noqa: WPS433
        import app.main as main_mod  # type: ignore
        client = TestClient(main_mod.app, raise_server_exceptions=False)
    except Exception as exc:  # noqa: BLE001
        out["reason"] = f"import failed: {type(exc).__name__}: {str(exc)[:120]}"
        print(json.dumps(out))
        return 0

    tenant_a = {"X-Tenant-Id": "tenant-a"}
    tenant_b = {"X-Tenant-Id": "tenant-b"}
    reasons: list[str] = []

    def body_of(resp) -> dict:
        try:
            b = resp.json()
            return b if isinstance(b, dict) else {}
        except Exception:  # noqa: BLE001
            return {}

    # correct
    r = client.post("/items", json={"name": "bolt", "quantity": 3}, headers=tenant_a)
    b = body_of(r)
    data = b.get("data") if isinstance(b.get("data"), dict) else {}
    created_ok = (r.status_code == 201 and b.get("status") == "success"
                  and data.get("name") == "bolt" and data.get("quantity") == 3)
    item_id = data.get("id")
    listed = client.get("/items", headers=tenant_a)
    lb = body_of(listed)
    in_list = any(isinstance(i, dict) and i.get("name") == "bolt" for i in (lb.get("data") or []))
    out["correct"] = int(created_ok and in_list)
    if not created_ok:
        reasons.append(f"create: status={r.status_code} body_keys={sorted(b)[:6]}")
    if not in_list:
        reasons.append("created item not listed for its tenant")
    out["reuse"] = int(b.get("status") == "success" and b.get("code") == "ITEM_CREATED")

    # safe: invalid payload must be a 4xx in the error envelope
    r_bad = client.post("/items", json={"name": "", "quantity": -1}, headers=tenant_a)
    bb = body_of(r_bad)
    invalid_rejected = r_bad.status_code in (400, 422) and bb.get("status") == "error"
    if not invalid_rejected:
        reasons.append(f"invalid payload answered {r_bad.status_code} status={bb.get('status')!r}")

    # safe: tenant isolation
    tenant_isolated = True
    if item_id is not None:
        r_b = client.get(f"/items/{item_id}", headers=tenant_b)
        lb_b = body_of(client.get("/items", headers=tenant_b))
        leaked = any(isinstance(i, dict) and i.get("id") == item_id for i in (lb_b.get("data") or []))
        tenant_isolated = r_b.status_code == 404 and not leaked
        if not tenant_isolated:
            reasons.append(f"tenant B sees tenant A's item (get={r_b.status_code}, listed={leaked})")

    # safe: no tenant header
    r_no = client.post("/items", json={"name": "nut", "quantity": 1})
    no_tenant_rejected = r_no.status_code == 401
    if not no_tenant_rejected:
        reasons.append(f"missing tenant header answered {r_no.status_code}")

    out["safe"] = int(invalid_rejected and tenant_isolated and no_tenant_rejected)
    out["reason"] = "; ".join(reasons) if reasons else "ok"
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
