from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, mapped_column, configure_mappers, lazyload, selectinload
from food_app.database import Base
from typing import List, Optional
from datetime import datetime
from enum import Enum


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



