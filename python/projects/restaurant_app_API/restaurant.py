from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import pandas as pd


engine = create_engine('url_for_the_databse')
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()

app = FastAPI(title='Food Delivery App', description='API for managing food delvery', version='1.0.0')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQL schema
class FoodServiceDB(Base):
    __tablename__ = 'restaurants'

    restaurant_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    cuisine = Column(String, nullable=False)

# Pydantic models
class FoodBase(BaseModel):
    name: str
    rating: float
    cuisine: str

class FoodOut(FoodBase):
    restaurant_id: int

    model_config = ConfigDict(from_attributes=True)


# endpoints
@app.get('/restaurants', response_model=List[FoodOut])
def get_restaurants(db: Session = Depends(get_db)):
    return db.query(FoodServiceDB).all()