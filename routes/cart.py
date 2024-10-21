from flask import request, jsonify
from models import db, Cart, Product, Order
from werkzeug.exceptions import BadRequest
from datetime import datetime

def add_to_cart() -> dict[str, str | dict[str, str | int]]:
    data = request.json
    existing_item = db.q('SELECT * FROM carts WHERE user_id = ? AND product_id = ?', 
                         (data['user_id'], data['product_id']))
    
    if existing_item:
        new_quantity = existing_item[0]['quantity'] + data['quantity']
        db.execute('UPDATE carts SET quantity = ? WHERE user_id = ? AND product_id = ?', 
                   (new_quantity, data['user_id'], data['product_id']))
        return jsonify({'message': 'Item quantity updated in cart'}), 200
    else:
        cart_item = Cart(user_id=data['user_id'], product_id=data['product_id'], quantity=data['quantity'])
        added_cart_item = db.t.carts.insert(cart_item)
        return jsonify({'message': 'Item added to cart', 'item': added_cart_item}), 201

def get_cart(user_id: int) -> dict[str, list | float]:
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

def delete_cart(user_id: int) -> dict[str, str]:
    # Delete all cart items for the user
    result = db.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
    
    if result.rowcount > 0:
        return jsonify({'message': 'Cart deleted successfully'}), 200
    else:
        return jsonify({'message': 'Cart is already empty'}), 200

def place_order(user_id: int) -> dict[str, str | int]:
    response = get_cart(user_id)
    if response[0].status_code != 200:
        return response
    
    # Check if the cart is empty
    cart_items = response[0].get_json()['items']
    if not cart_items:
        return jsonify({'error': 'Cart is empty, cannot place order'}), 400

    # Create an order for the user
    total_price = response[0].get_json()['total_price']
    for item in cart_items:
        # Check stock before updating
        check_stock = db.q("SELECT stock FROM products WHERE id = ?", (item['product_id'],))
        if not check_stock or check_stock[0]['stock'] < item['quantity']:
            return jsonify({'error': 'Insufficient stock for product ID: {}'.format(item['product_id'])}), 400
        
        # Update stock
        db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['quantity'], item['product_id']))
        product_response = db.q("SELECT stock FROM products WHERE id = ?", (item['product_id'],))

    order_date = datetime.now().isoformat()
    order = Order(user_id=user_id, items=cart_items, order_date=order_date, status='Pending')
    new_order = db.t.orders.insert(order)

    # Clear the cart after placing the order
    delete_cart(user_id)

    return jsonify({'message': 'Order placed successfully', 'order_id': new_order.id}), 201
