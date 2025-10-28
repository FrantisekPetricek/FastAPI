from fastapi import APIRouter, HTTPException, Depends
from app.users.schemas import User, UserGet, UserPost
from app.db import get_db
from sqlalchemy.orm import Session
from app.models import User as UserDB, Item as ItemDB


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserGet])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()

    return users


@router.post("/", response_model=UserPost)
async def create_user(user: UserPost, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.name == user.name).first()
    existing_email = db.query(UserDB).filter(UserDB.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_to_create = UserDB(**user.model_dump())

    db.add(user_to_create)
    db.commit()

    return user_to_create


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserPost, db: Session = Depends(get_db)):
    user_to_update = db.query(UserDB).filter(UserDB.id == user_id).first()

    if user_to_update is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.model_dump().items():
        setattr(user_to_update, key, value)

    db.commit()
    db.refresh(user_to_update)

    return user_to_update


@router.put("/{user_id}/{item_id}", response_model=UserGet)
async def update_user_items(user_id: int, item_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item not in user.items_bought:
        user.items_bought.append(item)
        db.commit()
        db.refresh(user)
    else:
        raise HTTPException(status_code=400, detail="User already owns this item")

    return user


@router.delete("/{user_id}", response_model=dict[str, str])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_to_delete = db.query(UserDB).filter(UserDB.id == user_id).first()

    if user_to_delete is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_name = user_to_delete.name
    db.delete(user_to_delete)
    db.commit()

    return {"message": f"User '{user_name}' was deleted"}


@router.delete("/{user_id}/{item_id}", response_model=dict[str, str])
async def delete_user_item(user_id: int, item_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item in user.items_bought:
        user.items_bought.remove(item)
        db.commit()
        db.refresh(user)
    else:
        raise HTTPException(status_code=400, detail="User does not own this item")

    return {"message": f"Item '{item.name}' was removed from user '{user.name}'"}
