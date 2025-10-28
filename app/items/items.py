from fastapi import APIRouter, HTTPException, Depends
from app.items.schemas import Item, ItemUpdate, ItemGet, ItemPost
from app.users.schemas import User
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db

from app.models import Item as ItemDB, User as UserDB

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemGet])
async def get_items(db: Session = Depends(get_db)):
    items = db.query(ItemDB).all()
    return items


@router.get("/price_avg")
async def get_item_price_avg(db: Session = Depends(get_db)) -> dict[str, float]:
    result = db.execute(select(ItemDB.price)).scalars().all()

    if not result:
        return {"price_avg": 0.0}

    avg = round(sum(result) / len(result), 2)
    return {"price_avg": avg}


@router.post("/", response_model=ItemPost)
async def create_item(item: Item, db: Session = Depends(get_db)):
    existing_item = db.query(ItemDB).filter(ItemDB.name == item.name).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists")

    item_to_create = ItemDB(**item.model_dump())

    db.add(item_to_create)
    db.commit()

    return item_to_create


@router.get("/{item_id}", response_model=ItemGet)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.execute(select(ItemDB).where(ItemDB.id == item_id)).scalars().first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

@router.get("/show_owner/{item_id}", response_model=List[User])
async def show_item_owner(item_id: int, db: Session = Depends(get_db)):

    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    owners = db.query(UserDB).filter(UserDB.items_bought.contains(item)).all()

    if owners is None:
        raise HTTPException(status_code=404, detail="Owners not found")

    return owners

@router.put("/{item_id}", response_model=ItemUpdate)
async def update_item(
    item_id: int, item: ItemUpdate, db: Session = Depends(get_db)
) -> Item:
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()

    return db_item


@router.delete("/{item_id}", response_model=dict[str, str])
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.execute(select(ItemDB).where(ItemDB.id == item_id)).scalars().first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item_name = item.name

    db.delete(item)
    db.commit()

    return {"message": f"Item '{item_name}' deleted successfully"}

