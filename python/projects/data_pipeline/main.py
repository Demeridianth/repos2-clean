from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import pandas as pd




# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --reload
# locust -f test_load_locust.py

# for test load
# --workers 4 → four separate processes

# --reload → optional for development

# Each worker will use its own connection pool, so total possible DB connections = workers * pool_size + max_overflow

# For 4 workers:

# Max persistent connections = 4 × 20 = 80

# Max temporary connections = 4 × 10 = 40

# Total max = 120 simultaneous DB connections


# ---------------------------
# Database setup
# ---------------------------
DATABASE_URL = 'postgresql://postgres:9922296@localhost:5432/dvd_rental'

engine = create_engine(
    DATABASE_URL,
    pool_size=30,        # persistent connections
    max_overflow=40,     # extra temporary connections
    pool_timeout=30,     # seconds to wait for a connection
    pool_pre_ping=True   # auto-check connections
)

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

    model_config = ConfigDict(from_attributes=True)

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

# search/query endpoint
@app.get('/films/search', response_model=List[FilmOut], tags=['Films'])
def search_films(
    # None = not required, if (..., min_length) = required
    min_year: Optional[int] = Query(None, description="Filter by minimum release year"),
    max_year: Optional[int] = Query(None, description="Filter by maximum release year"),
    title: Optional[str] = Query(None, description="Search by partial title"),
    db: Session = Depends(get_db)):
    """
    Search films by optional filters:
    - genre (partial match)
    - release year range
    - title (partial match)
    Example:
        /films/search?genre=Action&min_year=2010
    """

    query = db.query(FilmDB)

    if min_year:
        query = query.filter(FilmDB.release_year >= min_year)
    if max_year:
        query = query.filter(FilmDB.release_year <= max_year)
    if title:
        query = query.filter(FilmDB.title.ilike(f"%{title}%"))
    result = query.all()

    if not result:
        raise HTTPException(status_code=404, detail='No films match your search criteria')
    return result


# for debugging
def display_filtered_table():
    with engine.connect() as conn:
        query = """
        SELECT *
        FROM films
        WHERE release_year > 2010
        ORDER BY release_year
        LIMIT 5
        """
        df = pd.read_sql(query, conn)
        print(df)