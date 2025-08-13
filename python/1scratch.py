from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

DATABASE_URL = 'postgresql://postgres:9922296@localhost:5432/dvd_rental'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base()


class Filmbd(Base):
    __tablename__ = "transformed films"

    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    desciption = Column(String)
    release_year = Column(Integer)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "Data Pipeline API",
    description = "Api for data manipulation",
    version = "1.0.1"
)


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
