from dataclasses import dataclass
from fastlite import database
from enum import Enum
from werkzeug.security import generate_password_hash

db = database('data/ecommerce.db')

@dataclass
class User:
    id: int
    username: str
    password: str
    email: str
    role: str = 'user'

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    stock: int

@dataclass
class Cart:
    id: int
    user_id: int
    product_id: int
    quantity: int

@dataclass
class Order:
    id: int
    user_id: int
    cart_id: int
    order_date: str
    status: str

# Create tables
db.create(cls=User, name='users', pk='id', if_not_exists=True)
db.create(cls=Product, name='products', pk='id', if_not_exists=True)
db.create(cls=Cart, name='carts', pk='id', if_not_exists=True)
db.create(cls=Order, name='orders', pk='id', if_not_exists=True)

import json

def load_sample_products():
    with open('data/sample_products.json') as f:
        products = json.load(f)
        for product in products:
            db.t.products.insert(Product(**product))

def create_admin_user():
    admin_user = User(
        id=None,  
        username='admin',
        password=generate_password_hash('admin_password'),  
        email='admin@example.com',
        role='admin'
    )
    db.t.users.insert(admin_user)

# Call this function to create an admin user if it doesn't exist
if not db.q('SELECT * FROM users WHERE role = ?', ('admin',)):
    create_admin_user()

if __name__ == '__main__':
    print(db.t.users.columns)
