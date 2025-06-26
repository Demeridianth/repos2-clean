from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os

# SQLite Database setup
DATABASE_URL = "sqlite:///./films.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model
class FilmDB(Base):
    __tablename__ = "films"
    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    release_year = Column(Integer)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class Film(BaseModel):
    film_id: int
    title: str
    description: str
    release_year: int

    class Config:
        orm_mode = True

class FilmCreate(BaseModel):
    title: str
    description: str
    release_year: int

class FilmUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None

# FastAPI app
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/films", response_model=List[Film])
def get_films(db: Session = Depends(get_db)):
    return db.query(FilmDB).all()

@app.get("/films/{film_id}", response_model=Film)
def get_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film

@app.post("/films", response_model=Film)
def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    db_film = FilmDB(**film.dict())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

@app.put("/films/{film_id}", response_model=Film)
def update_film(film_id: int, updated: FilmUpdate, db: Session = Depends(get_db)):
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(film, key, value)
    db.commit()
    db.refresh(film)
    return film

@app.delete("/films/{film_id}", response_model=Film)
def delete_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    db.delete(film)
    db.commit()
    return film

@app.post("/ingest_csv/")
def ingest_csv(file_path: str, db: Session = Depends(get_db)):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="CSV file not found")
    df = pd.read_csv(file_path, delimiter='|')
    for _, row in df.iterrows():
        film = FilmDB(
            title=row['title'],
            description=row['description'],
            release_year=row['release_year']
        )
        db.add(film)
    db.commit()
    return {"message": "Ingestion complete"}
