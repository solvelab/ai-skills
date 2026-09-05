from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    quantity: int = Field(ge=0, le=1_000_000)


class ItemRead(BaseModel):
    id: int
    tenant_id: str
    name: str
    quantity: int
