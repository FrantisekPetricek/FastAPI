from pydantic import BaseModel, Field, EmailStr

from app.items.schemas import Item


class User(BaseModel):
    name: str = Field(...,example="John Doe", min_length=3, max_length=25)
    email: EmailStr = Field(
        ... , example="RZM8K@example.com", min_length=3, max_length=50
    )

class UserPost(User):
    password: str = Field(..., min_length=5, max_length=25)


class UserGet(User):
    items_bought: list[Item]
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"