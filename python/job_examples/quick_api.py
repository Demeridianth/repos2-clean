
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel 
from typing import List, Optional
from enum import Enum

# to run: uvicorn quick_api:app --reload --port 8000
# or
app = FastAPI(title='Products API')


class Quantity(Enum):
    in_stock = 'in stock'
    not_in_stock = 'not in stock'
    low_quantity = 'low quantity'


# Pydantic model
class Product(BaseModel):
    id: int
    name: str
    count: int
    quantity: Quantity

class ProductUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
    count: Optional[int]
    quantity: Optional[Quantity]

class ProductOut(Product):
    pass



# Data
products = {
    1: Product(id=1, name='keyboard', count=100, quantity=Quantity.in_stock),
    2: Product(id=2, name='mouse', count=0, quantity=Quantity.not_in_stock),
    3: Product(id=3, name='mouse_pad', count=2, quantity=Quantity.low_quantity)
}

@app.get('/products', response_model=List[ProductOut])
def get_all_products():
    return list(products.values())