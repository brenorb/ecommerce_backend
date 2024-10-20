from flask import request, jsonify
from models import db, Cart, Product

def add_to_cart():
    data = request.json
    cart_item = Cart(user_id=data['user_id'], product_id=data['product_id'], quantity=data['quantity'])
    added_cart_item = db.t.carts.insert(cart_item)
    return jsonify({'message': 'Item added to cart', 'item': added_cart_item}), 201

def get_cart(user_id):
    # Fetch cart items for the user
    cart_items = db.q('''
        SELECT c.id, c.user_id, c.product_id, c.quantity, p.name AS product_name, p.price
        FROM carts c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))
    if not cart_items:
        return jsonify({'message': 'Cart is empty', 'items': []}), 200

    # Calculate total price
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    # Format the response
    formatted_items = [
        {
            'id': item['id'],
            'product_id': item['product_id'],
            'product_name': item['product_name'],
            'quantity': item['quantity'],
            'price': item['price'],
            'subtotal': item['price'] * item['quantity']
        }
        for item in cart_items
    ]

    response = {
        'items': formatted_items,
        'total_price': total_price
    }

    return jsonify(response), 200

def delete_cart(user_id):
    # Delete all cart items for the user
    result = db.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
    
    if result.rowcount > 0:
        return jsonify({'message': 'Cart deleted successfully'}), 200
    else:
        return jsonify({'message': 'Cart is already empty'}), 200
