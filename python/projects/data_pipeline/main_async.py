from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# ---------------------------
# Database setup (async)
# ---------------------------
DATABASE_URL = "postgresql+asyncpg://postgres:9922296@localhost:5432/dvd_rental"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

# ---------------------------
# SQLAlchemy model          
# ---------------------------
# like a filter when connecting to Database
# maps to a database table to a Python class — for example, FilmDB → films.
# Lets you interact with the database using Python objects instead of raw SQL.
class FilmDB(Base):
    __tablename__ = "films"

    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)

# ---------------------------
# Pydantic models
# ---------------------------
# like a filter when connecting to a user/the frontend
# They handle data validation, conversion, and serialization —
# essentially, they make sure the data going in and out of your API is correct, clean, and safe.
class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None

class FilmCreate(FilmBase):
    pass

class FilmUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None

class FilmOut(FilmBase):
    film_id: int
    model_config = ConfigDict(from_attributes=True)

# ---------------------------
# Dependency
# ---------------------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="DVD Rental API (Async)",
    description="Async API for managing films in the DVD Rental database",
    version="2.0.0"
)

# ---------------------------
# CRUD endpoints (async)
# ---------------------------

@app.get("/films", response_model=List[FilmOut])
async def read_films(db: AsyncSession = Depends(get_db)):
    """Get all films"""
    result = await db.execute(select(FilmDB))
    films = result.scalars().all()
    return films

@app.get("/films/{film_id}", response_model=FilmOut)
async def read_film(film_id: int, db: AsyncSession = Depends(get_db)):
    """Get film by ID"""
    result = await db.execute(select(FilmDB).filter(FilmDB.film_id == film_id))
    film = result.scalar_one_or_none()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film

@app.post("/films", response_model=FilmOut)
async def create_film(film: FilmCreate, db: AsyncSession = Depends(get_db)):
    """Create new film"""
    new_film = FilmDB(**film.model_dump())
    db.add(new_film)
    await db.commit()
    await db.refresh(new_film)
    return new_film

@app.put("/films/{film_id}", response_model=FilmOut)
async def update_film(film_id: int, film: FilmUpdate, db: AsyncSession = Depends(get_db)):
    """Update film"""
    result = await db.execute(select(FilmDB).filter(FilmDB.film_id == film_id))
    db_film = result.scalar_one_or_none()
    if not db_film:
        raise HTTPException(status_code=404, detail="Film not found")
    update_data = film.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_film, key, value)
    await db.commit()
    await db.refresh(db_film)
    return db_film

@app.delete("/films/{film_id}", response_model=FilmOut)
async def delete_film(film_id: int, db: AsyncSession = Depends(get_db)):
    """Delete film"""
    result = await db.execute(select(FilmDB).filter(FilmDB.film_id == film_id))
    film = result.scalar_one_or_none()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    await db.delete(film)
    await db.commit()
    return film
