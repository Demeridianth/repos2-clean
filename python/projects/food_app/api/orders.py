from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from food_app.models.restaurant import RestaurantsDB, MenuDB
from fastapi import HTTPException
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from food_app.schemas.order import OrderOut, OrderCreate
from food_app.models.order import OrderDB, OrderItemDB, OrderStatus
from food_app.models.restaurant import RestaurantsDB, MenuDB
from food_app.database import get_db


router = APIRouter()


"""create and order, insert into orders table and order_items table"""
@router.post('/orders', response_model=OrderOut)
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
