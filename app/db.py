from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

DATABASE_URL = "mysql+pymysql://root:example@localhost:3306/test"

engine: Engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    echo=True,
)

sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = sessionmaker()
    try:
        yield db
    finally:
        db.close()


def initDB() -> None:
    Base.metadata.create_all(bind=engine)
