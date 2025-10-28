from pydantic import BaseModel, Field, EmailStr

from app.items.schemas import Item


class User(BaseModel):
    name: str = Field("John Doe", min_length=3, max_length=25)
    email: EmailStr = Field(
        "example@email.com", email=True, min_length=3, max_length=50
    )


class UserPost(User):
    pass


class UserGet(User):
    items_bought: list[Item]
    id: int
