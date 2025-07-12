from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# === Database Configuration ===
DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/films_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# === SQLAlchemy Model ===
class FilmDB(Base):
    __tablename__ = "films"

    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)

# === FastAPI App ===
app = FastAPI()

# === Dependency ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Pydantic Models ===
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

# === CRUD Endpoints ===
@app.get("/films", response_model=List[FilmOut])
def read_films(db: Session = Depends(get_db)):
    return db.query(FilmDB).all()

@app.get("/films/{film_id}", response_model=FilmOut)
def read_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film

@app.post("/films", response_model=FilmOut)
def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    new_film = FilmDB(**film.dict())
    db.add(new_film)
    db.commit()
    db.refresh(new_film)
    return new_film

@app.put("/films/{film_id}", response_model=FilmOut)
def update_film(film_id: int, film: FilmUpdate, db: Session = Depends(get_db)):
    db_film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not db_film:
        raise HTTPException(status_code=404, detail="Film not found")
    update_data = film.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_film, key, value)
    db.commit()
    db.refresh(db_film)
    return db_film

@app.delete("/films/{film_id}", response_model=FilmOut)
def delete_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(FilmDB).filter(FilmDB.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    db.delete(film)
    db.commit()
    return film
