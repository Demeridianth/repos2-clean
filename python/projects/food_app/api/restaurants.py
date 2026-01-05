from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from food_app.models.restaurant import RestaurantsDB, MenuDB
from fastapi import HTTPException
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from food_app.schemas.restaurant import RestaurantOut, MenuOut
from food_app.database import get_db

router = APIRouter()


"""get all restaurants"""
@router.get('/restaurants', response_model=List[RestaurantOut])
async def get_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RestaurantsDB))
    restaurants = result.scalars().all()
    # scalars transform tuples into simple values
    return restaurants

"""get all dishes from a restaurant by id"""
@router.get('/restaurants/{restaurant_id}/menu', response_model=List[MenuOut])
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