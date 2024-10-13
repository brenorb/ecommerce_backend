from flask import jsonify
from models import db, Product

def get_products():
    products = db.q('SELECT * FROM products')
    return jsonify(products), 200

# Add more product-related routes here (e.g., add_product, update_product, delete_product)
