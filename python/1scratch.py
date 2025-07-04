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
# Base.metadata.create_all(bind=engine)     