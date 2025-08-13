from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

# ---------------------------
# Database setup
# ---------------------------
DATABASE_URL = 'postgresql://postgres:9922296@localhost:5432/dvd_rental'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------
# SQLAlchemy model
# ---------------------------
class FilmDB(Base):
    __tablename__ = "films"

    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="DVD Rental API",
    description="API for managing films in the DVD Rental database",
    version="1.0.0"
)

# ---------------------------
# Pydantic models
# ---------------------------
class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None

class FilmCreate(FilmBase):
    pass

class FilmUpdate(BaseModel):  # no inheritance, all optional for PATCH-like updates
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None

class FilmOut(FilmBase):
    film_id: int

    class Config:
        orm_mode = True

# ---------------------------
# Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# CRUD endpoints
# ---------------------------
@app.get('/films', response_model=List[FilmOut], tags=["Films"])
def read_films(db: Session = Depends(get_db)):
    """Get a list of all films."""
    return db.query(FilmDB).all()

@app.get('/films/{film_id}', response_model=FilmOut, tags=["Films"])
def read_film(film_id: int, db: Session = Depends(get_db)):
    """Get a single film by ID."""
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')
    return film

@app.post('/films', response_model=FilmOut, tags=["Films"])
def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    """Add a new film."""
    new_film = FilmDB(**film.model_dump())
    db.add(new_film)
    db.commit()
    db.refresh(new_film)
    return new_film

@app.put('/films/{film_id}', response_model=FilmOut, tags=["Films"])
def update_film(film_id: int, film: FilmUpdate, db: Session = Depends(get_db)):
    """Update an existing film."""
    db_film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not db_film:
        raise HTTPException(status_code=404, detail='Film not found')
    update_data = film.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_film, key, value)
    db.commit()
    db.refresh(db_film)
    return db_film

@app.delete('/films/{film_id}', response_model=FilmOut, tags=["Films"])
def delete_film(film_id: int, db: Session = Depends(get_db)):
    """Delete a film."""
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')
    db.delete(film)
    db.commit()
    return film

@app.post('/films/inject_csv', response_model=List[FilmOut], tags=["Films"])
def inject_csv(db: Session = Depends(get_db)):
    """
    Inject sample data from 'films_pipe.csv'.
    Only first 5 rows are inserted.
    """
    df = pd.read_csv('films_pipe.csv', delimiter='|').iloc[:, :4].head()
    injected = []
    for row in df.itertuples(index=False):
        film = FilmDB(
            title=row.title,
            description=row.description,
            release_year=row.release_year
        )
        db.add(film)
        injected.append(film)
    db.commit()
    for film in injected:
        db.refresh(film)
    return injected
