from dataclasses import dataclass
from fastlite import database

db = database('data/ecommerce.db')

@dataclass
class User:
    user_id: int
    username: str
    password: str
    email: str

@dataclass
class Product:
    product_id: int
    name: str
    description: str
    price: float
    stock: int

@dataclass
class Cart:
    cart_id: int
    user_id: int
    product_id: int
    quantity: int

@dataclass
class Order:
    order_id: int
    user_id: int
    cart_id: int
    order_date: str
    status: str

# Create tables
db.create(cls=User, name='users', pk='user_id', if_not_exists=True)
db.create(cls=Product, name='products', pk='product_id', if_not_exists=True)
db.create(cls=Cart, name='carts', pk='cart_id', if_not_exists=True)
db.create(cls=Order, name='orders', pk='order_id', if_not_exists=True)

import json

def load_sample_products():
    with open('data/sample_products.json') as f:
        products = json.load(f)
        for product in products:
            db.t.products.insert(Product(**product))
