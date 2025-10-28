from fastapi import FastAPI
from app.users.users import router as user_router
from app.items.items import router as item_router

from app.db import initDB

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

initDB()

app.include_router(user_router)
app.include_router(item_router)


