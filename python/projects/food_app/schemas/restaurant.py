from pydantic import BaseModel, ConfigDict
from typing import Optional, List


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