"""In-memory item store. Every query is scoped by tenant_id: an item is never visible to another
tenant, and the tenant comes from the request context, never from the payload."""
from __future__ import annotations


class ItemRepository:
    def __init__(self) -> None:
        self._items: dict[int, dict] = {}
        self._next_id = 1

    def list(self, tenant_id: str) -> list[dict]:
        return [dict(i) for i in self._items.values() if i["tenant_id"] == tenant_id]

    def get(self, tenant_id: str, item_id: int) -> dict | None:
        item = self._items.get(item_id)
        if item is None or item["tenant_id"] != tenant_id:
            return None
        return dict(item)

    def create(self, tenant_id: str, name: str, quantity: int) -> dict:
        item = {"id": self._next_id, "tenant_id": tenant_id, "name": name, "quantity": quantity}
        self._items[item["id"]] = item
        self._next_id += 1
        return dict(item)


repository = ItemRepository()
