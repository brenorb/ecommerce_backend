from flask import jsonify, request, session
from models import db, Product

def get_products():
    products = db.q('SELECT * FROM products')
    return jsonify(products), 200

def get_product_by_id(product_id):
    product = db.q('SELECT * FROM products WHERE id = ?', (product_id,))
    if product:
        return jsonify(product), 200
    else:
        return jsonify({'error': 'Product not found'}), 404

def add_product():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized: Admins only'}), 403

    data = request.json
    new_product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        stock=data['stock']
    )
    new_row = db.t.products.insert(new_product)

    return jsonify({'message': 'Product added successfully', 'product': new_row}), 201

def update_product(product_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized: Admins only'}), 403

    data = request.json
    result = db.execute('UPDATE products SET name = ?, description = ?, price = ?, stock = ? WHERE id = ?',
                        (data['name'], data['description'], data['price'], data['stock'], product_id))
    
    if result.rowcount > 0:
        return jsonify({'message': 'Product updated successfully'}), 200
    else:
        return jsonify({'error': 'Product not found'}), 404

def delete_product(product_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized: Admins only'}), 403

    result = db.execute('DELETE FROM products WHERE id = ?', (product_id,))
    
    if result.rowcount > 0:
        return jsonify({'message': 'Product deleted successfully'}), 200
    else:
        return jsonify({'error': 'Product not found'}), 404
