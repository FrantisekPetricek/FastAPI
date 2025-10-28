from sqlalchemy import Column, Float, String, Integer, Table, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(length=21), nullable=False, unique=True)
    description = Column(String(length=255), nullable=False)
    price = Column(Float, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(length=25), nullable=False, unique=True)
    email = Column(String(length=50), nullable=False, unique=True)

    items_bought = relationship("Item", secondary="user_items", back_populates="buyers")


user_items = Table(
    "user_items",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("item_id", Integer, ForeignKey("items.id")),
)

Item.buyers = relationship(
    "User", secondary="user_items", back_populates="items_bought"
)
