from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict
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
# class FilmDB(Base):
#     __tablename__ = "films"

#     film_id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     description = Column(String)
#     release_year = Column(Integer)

def display_table():
    with engine.connect() as conn:
        df = pd.read_sql('SELECT * FROM film LIMIT 5', conn)
        print(df)

display_table()
