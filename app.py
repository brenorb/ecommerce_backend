import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from fastlite import database
from dataclasses import dataclass
from routes import auth, products, cart
from models import db, load_sample_products

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'your-secret-key-here'

# Check if the products table is empty and load sample products if it is
result = db.q(f'SELECT COUNT(*) AS enum FROM products')
if result[0]['enum'] == 0:
    load_sample_products()

@app.route("/", methods=['GET'])
def home():
    # Just for testing
    return "API running"

# Auth routes
app.route('/v1/register', methods=['POST'])(auth.register)
app.route('/v1/login', methods=['POST'])(auth.login)
app.route('/v1/logout', methods=['POST'])(auth.logout)
app.route('/v1/user/<str:username>', methods=['DELETE'])(auth.delete_user)
app.route('/v1/user/<str:username>', methods=['GET'])(auth.get_user)  

# Product routes
app.route('/v1/products', methods=['GET'])(products.get_products)
app.route('/v1/products', methods=['POST'])(products.add_product)  
app.route('/v1/products/<int:product_id>', methods=['GET'])(products.get_product_by_id)
app.route('/v1/products/<int:product_id>', methods=['PUT'])(products.update_product)
app.route('/v1/products/<int:product_id>', methods=['DELETE'])(products.delete_product)

# Cart routes
app.route('/v1/cart', methods=['POST'])(cart.add_to_cart)
app.route('/v1/cart/<int:user_id>', methods=['GET'])(cart.get_cart)
app.route('/v1/cart/<int:user_id>', methods=['DELETE'])(cart.delete_cart)
app.route('/v1/order/<int:user_id>', methods=['POST'])(cart.place_order)


if __name__ == '__main__':
    app.run()
