from flask import request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

def register():
    data = request.json
    result = db.q('SELECT COUNT(*) AS enum FROM users WHERE username = ? OR email = ?', 
                  (data["username"], data["email"]))
    existing_user = result[0]['enum'] > 0
    if existing_user:
        return jsonify({'error': 'Conflict: username or email already exists'}), 409
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password, email=data['email'])
    db.t.users.insert(user)
    return jsonify({'message': 'User created successfully'}), 201

def login():
    data = request.json
    user = db.q('SELECT * FROM users WHERE username = ?', (data["username"],))
    if user and check_password_hash(user[0]['password'], data['password']):
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Unauthorized'}), 401

def delete_user(username):
    result = db.execute("DELETE FROM users WHERE username = ?", (username,))
    if result.rowcount > 0:
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404
