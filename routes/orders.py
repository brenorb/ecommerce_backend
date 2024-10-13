from flask import request, jsonify
from models import db, Order

def place_order():
    data = request.json
    order = Order(user_id=data['user_id'], cart_id=data['cart_id'])
    db.t.orders.insert(order)
    cart = db.q('SELECT * FROM carts WHERE user_id = ?', (data['user_id'],))
    if cart:
        db.t.carts.delete(cart[0]['cart_id'])
    return jsonify({'message': 'Order placed successfully'}), 201

# Add more order-related routes here (e.g., get_orders, update_order_status)
