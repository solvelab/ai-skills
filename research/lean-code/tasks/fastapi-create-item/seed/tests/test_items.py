from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
TENANT_A = {"X-Tenant-Id": "tenant-a"}


def test_list_returns_envelope():
    r = client.get("/items", headers=TENANT_A)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "success" and body["code"] == "ITEMS_LISTED"
    assert isinstance(body["data"], list)


def test_missing_tenant_header_is_401_in_envelope():
    r = client.get("/items")
    assert r.status_code == 401
    assert r.json()["status"] == "error"


def test_unknown_item_is_404_in_envelope():
    r = client.get("/items/999", headers=TENANT_A)
    assert r.status_code == 404
    assert r.json()["code"] == "NOT_FOUND"
