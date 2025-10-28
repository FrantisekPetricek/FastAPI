from pydantic import BaseModel, Field, ConfigDict

class Item(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=21)
    description: str | None = Field(None, min_length=6, max_length=100)
    price: float | None  = Field(None, gt=0, le=1000)

    model_config = ConfigDict(from_attributes=True)

class ItemPost(Item):
    pass

class ItemGet(Item):
    id: int

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None  = None

