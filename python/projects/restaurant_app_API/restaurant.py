from fastapi import FastAPI, HTTPException, Depends, Path
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


# Restaurants
class RestaurantsDB(Base):
    __tablename__ = "restaurants"

    restaurant_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    cuisine: Mapped[str] = mapped_column(String, nullable=False)

    # 1 restaurant -> many menus
    menus: Mapped[List['MenuDB']] = relationship(back_populates='restaurant', cascade='all, delete_orphan')
    # all, delete_orphan = “When I add, update, or delete a Restaurant, apply those operations to related Menu rows automatically.”
    # “If a Menu item no longer belongs to any Restaurant, DELETE it from the DB automatically.”

# Menus
class MenuDB(Base):
    __tablename__ = "menus"

    dish_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dish_name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    optional_description: Mapped[str | None] = mapped_column(String)

     # FK to restaurants table
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurants.restaurant_id'), nullable=False)

    # Many manus -> 1 restaurant
    restaurant: Mapped['RestaurantsDB'] = relationship(back_populates='menus')



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
    dish_name: str
    price: float
    optional_description: Optional[str]

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    dish_name: Optional[str]
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
    """get all restaurants"""
    result = await db.execute(select(RestaurantsDB))
    restaurants = result.scalars().all()
    # scalars transform tuples into simple values
    return restaurants

@app.get('/restaurants/{id}/menu', response_model=List[MenuOut])
async def get_restaurant_menu(restaurant_id: int = Path(..., title='ID of the restaurant'), db: AsyncSession = Depends(get_db)):
    """get all dishes from a restaurant by id"""

    # Optional: check if restaurant exists first
    result = await db.execute(
        select(RestaurantsDB).where(RestaurantsDB.restaurant_id == restaurant_id)
    )
    restaurant = result.scalar_one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    result = await db.execute(select(MenuDB).where(MenuDB.restaurant_id == restaurant_id))
    menu = result.scalars().all()
    if not menu:
        return []
    return menu