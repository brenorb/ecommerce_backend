import json
from flask import Flask, request, jsonify
# from flask_basicauth import BasicAuth
from fastlite import database
from dataclasses import dataclass
from routes import auth, products, cart, orders
from models import db, load_sample_products

app = Flask(__name__)

# Check if the products table is empty and load sample products if it is
result = db.q(f'SELECT COUNT(*) AS enum FROM products')
if result[0]['enum'] == 0:
    load_sample_products()

@app.route("/", methods=['GET'])
def home():
    return "<h1>API running</h1>"

# Auth routes
app.route('/v1/register', methods=['POST'])(auth.register)
app.route('/v1/login', methods=['POST'])(auth.login)
app.route('/v1/user/<username>', methods=['DELETE'])(auth.delete_user)

# Product routes
app.route('/v1/products', methods=['GET'])(products.get_products)

# Cart routes
app.route('/v1/cart', methods=['POST'])(cart.add_to_cart)

@app.route('/v1/cart/<int:user_id>', methods=['GET'])
def get_user_cart(user_id):
    return cart.get_cart(user_id)

@app.route('/v1/cart/delete/<int:user_id>', methods=['DELETE'])
def delete_user_cart(user_id):
    return cart.delete_cart(user_id)

# Order routes
app.route('/v1/order', methods=['POST'])(orders.place_order)


if __name__ == '__main__':
    app.run(debug=True)
