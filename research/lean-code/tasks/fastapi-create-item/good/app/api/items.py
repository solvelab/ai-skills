from fastapi import APIRouter, Depends

from app.api.dependencies import get_tenant_id
from app.core.exceptions import NotFoundException
from app.core.response_codes import ResponseCodes as RC
from app.repositories.item_repository import repository
from app.schemas.common import success
from app.schemas.item import ItemCreate, ItemRead

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
def list_items(tenant_id: str = Depends(get_tenant_id)) -> dict:
    items = [ItemRead(**i).model_dump() for i in repository.list(tenant_id)]
    return success(RC.ITEMS_LISTED, "Items listed", items)


@router.get("/{item_id}")
def get_item(item_id: int, tenant_id: str = Depends(get_tenant_id)) -> dict:
    item = repository.get(tenant_id, item_id)
    if item is None:
        raise NotFoundException("Item not found")
    return success(RC.ITEM_FOUND, "Item found", ItemRead(**item).model_dump())


@router.post("", status_code=201)
def create_item(body: ItemCreate, tenant_id: str = Depends(get_tenant_id)) -> dict:
    item = repository.create(tenant_id, body.name, body.quantity)
    return success(RC.ITEM_CREATED, "Item created", ItemRead(**item).model_dump())
