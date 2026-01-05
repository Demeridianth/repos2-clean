from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column, configure_mappers, lazyload, selectinload
from food_app.database import Base
from typing import List, Optional


# Restaurants
class RestaurantsDB(Base):
    __tablename__ = "restaurants"

    restaurant_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    restaurant_name: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    cuisine: Mapped[str] = mapped_column(String, nullable=False)

    # 1 restaurant -> many menus
    menus: Mapped[List['MenuDB']] = relationship(
        back_populates='restaurant', 
        cascade='all, delete-orphan', 
        single_parent=True, 
        lazy='selectin')
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

