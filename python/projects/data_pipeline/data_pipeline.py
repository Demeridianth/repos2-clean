from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os

# SQLite Database setup
DATABASE_URL = 'postgresql://postgres:9922296@localhost:5432/dvd_rental'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy model
class FilmDB(Base):
    __tablename__ = "films"

    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)

# IF THE TABLE DOESNT EXIST YET IN THE DATABASE
Base.metadata.create_all(bind=engine)     


# FastApi app
app = FastAPI()


# Pydantic models:

# FilmBase → Shared fields

# FilmCreate → POST input

# FilmUpdate → PUT input

# FilmOut → GET response


class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None

class FilmCreate(FilmBase):
    pass

class FilmUpdate(FilmBase):
    title: Optional[str] = None

class FilmOut(FilmBase):
    film_id: int

    class Config:
        orm_mode = True


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD endpoint

@app.get('/films', response_model=List[FilmOut])
def read_films(db: Session = Depends(get_db)):
    return db.query(FilmDB).all()

@app.get('/films/{film_id}', response_model=FilmOut)
def read_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id)
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')
    return film

@app.post('/films', response_model=FilmOut)
def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    new_film = FilmDB(**film.model_dump())
    db.add(new_film)
    db.commit()
    db.refresh(new_film)
    return new_film

@app.put('/films/{film_id}', response_model=FilmOut)
def update_film(film_id: int, film: FilmUpdate, db: Session = Depends(get_db)):
    db_film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not db_film:
        raise HTTPException(status_code=404, detail='Film not found')
    update_data = film.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_film, key, value)
    db.commit()
    db.refresh(db_film)
    return db_film

@app.delete('/films/{film_id}', response_model=FilmOut)
def delete_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail='Film not found')
    db.delete(film)
    db.commit()
    return film

@app.post('/inject_csv', response_model=List[FilmOut])
def inject_csv(db: Session = Depends(get_db)):
    df = pd.read_csv('films_pipe.csv', delimiter='|').iloc[:, :4].head()
    injected = []
    for row in df.itertuples(index=False):
        film = FilmDB(
            title = row.title,
            description = row.description,
            release_year = row.release_year
        )
        db.add(film)
        injected.append(film) 
    db.commit()
    for film in injected:
        db.refresh(film)
    return injected
 