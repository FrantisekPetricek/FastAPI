from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.users.schemas import User, UserGet, UserPost, Token
from app.items.schemas import ItemGet
from app.db import get_db
from sqlalchemy.orm import Session
from app.models import User as UserDB, Item as ItemDB
from app.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from jose import JWTError, jwt

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exeptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exeptions

    except JWTError:
        raise credentials_exeptions

    user = db.query(UserDB).filter(UserDB.email == email).first()

    if user is None:
        raise credentials_exeptions

    return user


@router.get("/", response_model=list[UserGet])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()

    return users


@router.post("/", response_model=UserGet)
async def create_user(user: UserPost, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.name == user.name).first()
    existing_email = db.query(UserDB).filter(UserDB.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_to_create = UserDB(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    db.add(user_to_create)
    db.commit()

    return user_to_create


@router.get("/me", response_model=UserGet)
async def read_current_user(current_user: UserDB = Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(UserDB.email == form_data.username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/{user_id}", response_model=User)
async def update_user(
    user: User,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_user = db.query(UserDB).filter(UserDB.name == user.name).first()
    existing_email = db.query(UserDB).filter(UserDB.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    for key, value in user.model_dump().items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.put("/{user_id}/{item_id}", response_model=UserGet)
async def update_user_items(
    item_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item not in user.items_bought:
        user.items_bought.append(item)
        db.commit()
        db.refresh(user)
    else:
        raise HTTPException(status_code=400, detail="User already owns this item")

    return user


@router.delete("/delete", response_model=dict[str, str])
async def delete_user(
    current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_name = current_user.name
    db.delete(current_user)
    db.commit()

    return {"message": f"User '{user_name}' was deleted"}


@router.delete("/items/delete/{item_id}", response_model=dict[str, str])
async def delete_user_item(
    item_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item in current_user.items_bought:
        current_user.items_bought.remove(item)
        db.commit()
        db.refresh(current_user)
    else:
        raise HTTPException(status_code=400, detail="User does not own this item")

    return {
        "message": f"Item '{item.name}' was removed from user '{current_user.name}'"
    }


@router.get("/items", response_model=list[ItemGet])
async def get_user_items(
    current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)
):
    if len(current_user.items_bought) == 0:
        raise HTTPException(status_code=404, detail="User has no items")

    return current_user.items_bought
