from fastapi import FastAPI, HTTPException, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column, configure_mappers, lazyload, selectinload
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

"""structure (maybe with routers), next sprint"""


# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="Food Service API",
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
    allow_credentials=True,  # Allow cookies or authentication headers
)


# ---------------------------
# Database setup (async)
# ---------------------------
DATABASE_URL = 'postgresql+asyncpg://postgres:9922296@localhost:5432/food'
engine = create_async_engine(DATABASE_URL, future=True)     # can add 'echo=True' for debuging, will show SQL quearies in terminal
AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


# ---------------------------
# SQLAlchemy models       
# ---------------------------

# Restaurants
class RestaurantsDB(Base):
    __tablename__ = "restaurants"

    restaurant_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    restaurant_name: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    cuisine: Mapped[str] = mapped_column(String, nullable=False)

    # 1 restaurant -> many menus
    menus: Mapped[List['MenuDB']] = relationship(back_populates='restaurant', cascade='all, delete-orphan', single_parent=True, lazy='selectin')
    # all, delete_orphan = “When I add, update, or delete a Restaurant, apply those operations to related Menu rows automatically.”
    # “If a Menu item no longer belongs to any Restaurant, DELETE it from the DB automatically.”
    # SINGLE PARENT means = “A child object can only ever belong to ONE parent at a time.” t means each MenuDB item can be linked to only one restaurant IT IS NEEDED FOR 'all, delete-orphan'

    orders: Mapped[List['OrderDB']] = relationship(back_populates='restaurant', lazy='selectin')

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
    restaurant: Mapped['RestaurantsDB'] = relationship(back_populates='menus', lazy='selectin')
    items: Mapped[List['OrderItemDB']] = relationship(back_populates='dish', lazy='selectin')

# Orders
class OrderStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    delivered = "delivered"
    cancelled = "cancelled"

class OrderDB(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    status: Mapped[str] = mapped_column(
        SAEnum(OrderStatus, name='order_status_enum'), 
        nullable=False,
        default=OrderStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  
    customer_id: Mapped[int] = mapped_column(nullable=False)  
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurants.restaurant_id'), nullable=False)
    delivery_address: Mapped[str] = mapped_column(String, nullable=False)  
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)  

    items: Mapped[List['OrderItemDB']] = relationship(back_populates='order', cascade='all, delete-orphan', single_parent=True, lazy='selectin')
    restaurant: Mapped['RestaurantsDB'] = relationship(back_populates='orders', lazy='selectin')

# Order Items
class OrderItemDB(Base):
    __tablename__ = "order_items"

    item_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id'), nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey('menus.dish_id'), nullable=False)

    order: Mapped['OrderDB'] = relationship(back_populates='items', lazy='selectin')
    dish: Mapped['MenuDB'] = relationship(back_populates='items', lazy='selectin')



# ---------------------------
# Pydantic models
# ---------------------------

# ---------------------------
# Restaurants
# ---------------------------
class RestaurantBase(BaseModel):
    restaurant_name: str
    rating: float
    cuisine: str

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    restaurant_name: Optional[str]
    rating: Optional[float]
    cuisine: Optional[str]

class RestaurantOut(RestaurantBase):
    restaurant_id: int
    model_config = ConfigDict(from_attributes=True)

# ---------------------------
# Menus
# ---------------------------
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
# Orders
# ---------------------------
class OrderItemCreate(BaseModel):
    quantity: int
    dish_id: int = Field(gt=0)      # so this wont be allowed: { "dish_id": 1, "quantity": -10 }

class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    delivery_address: str
    payment_method: str
    items: List[OrderItemCreate]

class OrderOut(BaseModel):
    order_id: int
    status: OrderStatus
    total_price: float
    delivery_adress: str

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
"""get all restaurants"""
@app.get('/restaurants', response_model=List[RestaurantOut])
async def get_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RestaurantsDB))
    restaurants = result.scalars().all()
    # scalars transform tuples into simple values
    return restaurants

"""get all dishes from a restaurant by id"""
@app.get('/restaurants/{restaurant_id}/menu', response_model=List[MenuOut])
async def get_restaurant_menu(restaurant_id: int = Path(..., title='ID of the restaurant'), db: AsyncSession = Depends(get_db)):    
    #Path is optional
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



"""create and order, insert into orders table and order_items table"""
@app.post('/orders', response_model=OrderOut)
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):

    dish_ids = [item.dish_id for item in order_data.items]

    # START TRANSACTION - db.begin()
    # If everything inside succeeds → COMMIT
    # If ANY exception happens → ROLLBACK automatically
    async with db.begin():
        restaurant = await db.scalar(
            select(RestaurantsDB)
            .where(RestaurantsDB.restaurant_id == order_data.restaurant_id)
        )
        # Check if restaurant exists
        if not restaurant:
            raise HTTPException(404, "Restaurant not found")
        # Get all dishes in request
        dishes = (
            await db.scalars(
                select(MenuDB).where(
                    MenuDB.dish_id.in_(dish_ids),
                    MenuDB.restaurant_id == order_data.restaurant_id
                )
            )
        ).all()

        if len(dishes) != len(dish_ids):
            raise HTTPException(400, "Invalid dishes")

        # map dish_id - > price
        price_map = {d.dish_id: d.price for d in dishes}

        # calculate total price
        total_price = sum(
            price_map[item.dish_id] * item.quantity
            for item in order_data.items
        )

        # create order
        order = OrderDB(
            customer_id=order_data.customer_id,
            restaurant_id=order_data.restaurant_id,
            delivery_address=order_data.delivery_address,
            payment_method=order_data.payment_method,
            status=OrderStatus.pending,
            total_price=total_price
        )
        db.add(order)
        await db.flush()

        # create order_items
        for item in order_data.items:
            db.add(
                OrderItemDB(
                    order_id=order.order_id,
                    dish_id=item.dish_id,
                    quantity=item.quantity
                )
            )

    return OrderOut(
        order_id=order.order_id,
        status=order.status,
        total_price=order.total_price,
        delivery_adress=order.delivery_address
    )
