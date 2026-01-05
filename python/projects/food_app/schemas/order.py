from pydantic import BaseModel, ConfigDict, Field
from typing import List
from enum import Enum


# ---------------------------
# Orders
# ---------------------------
class OrderStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    delivered = "delivered"
    cancelled = "cancelled"

class OrderItemCreate(BaseModel):
    quantity: int = Field(gt=0)
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