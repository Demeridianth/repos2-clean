from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, ConfigDict
from typing import List, Optional


# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="Food Servie API",
    description="Async API for food service",
    version="1.0.0"
)


# ======================
# CORS for frontend dev
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # In production, set your frontend URL, like   allow_origins=["https://myfrontend.com"]
    allow_methods=["*"],    # Which HTTP methods are allowed (GET, POST, etc.)
    allow_headers=["*"],    # Which headers are allowed (like Authorization)
    allow_credential=True,  # Allow cookies or authentication headers
)


# ---------------------------
# Database setup (async)
# ---------------------------
DATABASE_URL = 'postgresql+asyncpg://postgres:9922296@localhost:5432/food'
engine = create_async_engine(DATABASE_URL, future=True)     # can add 'echo=True' for debuging, will show SQL quearies in terminal
AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_=AsyncSession)
Base = declarative_base()


# ---------------------------
# SQLAlchemy models       
# ---------------------------

""" ADD NEW Mapped, mapped_column, """
""" ADD relationship, foreign_key"""
""" CREATE menus table in Postgres"""

# Restaurants
class RestaurantsDB(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    cuisine = Column(String, nullable=False)

    manus = relationship('MenuDB', back_populates='restaurants')

# Menus
class MenuDB(Base):
    __tablename__ = "menus"

    dish_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    optional_description = Column(String)



# ---------------------------
# Pydantic models
# ---------------------------

# Restaurants
class RestaurantBase(BaseModel):
    name: str
    rating: float
    cuisine: str

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name: Optional[str]
    rating: Optional[float]
    cuisine: Optional[str]

class RestaurantOut(RestaurantBase):
    restaurant_id: int
    model_config = ConfigDict(from_attributes=True)

# Menus
class MenuBase(BaseModel):
    name: str
    price: float
    optional_description: Optional[str]

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    name: Optional[str]
    price: Optional[float]
    optional_description: Optional[str]

class MenuOut(MenuBase):
    dish_id: int
    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Dependency
# ---------------------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------
# CRUD endpoints (async)
# ---------------------------

@app.get('/restaurants', response_model=List[RestaurantOut])
async def get_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RestaurantsDB))
    restaurants = result.scalars().all
    return restaurants

@app.get('restaurants/{id}/menu', response_model=List[MenuOut])
async def get_restaurant_menu(restaurant_id: int,  db: AsyncSession = Depends(get_db)):
