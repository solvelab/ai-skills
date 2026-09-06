from pydantic import BaseModel


class ItemRead(BaseModel):
    id: int
    tenant_id: str
    name: str
    quantity: int
