# app/
# │
# ├── main.py               # Starts the app (FastAPI instance)
# ├── database.py           # Database connection + Base
# ├── models.py             # SQLAlchemy ORM models
# ├── schemas.py            # Pydantic models (request/response validation)
# ├── crud.py               # CRUD logic (db queries)
# ├── routers/
# │   ├── films.py          # Endpoints related to films
# │   └── users.py          # (later) endpoints related to users
# └── tests/
#     └── test_films.py     # Pytest tests


"""database.py"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:9922296@localhost:5432/dvd_rental"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


"""models.py"""
from sqlalchemy import Column, Integer, String
from .database import Base

class FilmDB(Base):
    __tablename__ = "films"
    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)


"""schemas.py"""
from pydantic import BaseModel
from typing import Optional

class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None

class FilmOut(FilmBase):
    film_id: int

    class Config:
        orm_mode = True


"""main.py"""
from fastapi import FastAPI, Depends
from .database import Base, engine
from .models import FilmDB
from .routers import films

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DVD Rental API")
app.include_router(films.router)


"""routers/films.py"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import FilmDB
from ..schemas import FilmOut

router = APIRouter(prefix="/films", tags=["Films"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[FilmOut])
def read_films(db: Session = Depends(get_db)):
    return db.query(FilmDB).all()

