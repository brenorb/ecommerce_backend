from flask import request, jsonify, session
from models import db, User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash

def register():
    data = request.json
    result = db.q('SELECT COUNT(*) AS enum FROM users WHERE username = ? OR email = ?', 
                  (data['username'], data['email']))
    existing_user = result[0]['enum'] > 0
    if existing_user:
        return jsonify({'error': 'Conflict: username or email already exists'}), 409
    hashed_password = generate_password_hash(data['password'])
    role = UserRole.ADMIN if data.get('is_admin') else UserRole.USER
    user = User(username=data['username'], password=hashed_password, email=data['email'], role=role)
    db.t.users.insert(user)
    return jsonify({'message': 'User registered successfully'}), 201

def login():
    data = request.json
    user = db.q('SELECT * FROM users WHERE username = ?', (data['username'],))
    if user and check_password_hash(user[0]['password'], data['password']):
        session['username'] = user[0]['username']
        session['role'] = user[0]['role']  # Store user role in session
        return jsonify({'message': 'Login successful', 'role': user[0]['role']}), 200
    return jsonify({'error': 'Unauthorized'}), 401

def delete_user(username):
    if 'role' in session and session['role'] == UserRole.ADMIN.value:
        result = db.execute('DELETE FROM users WHERE username = ?', (username,))
        if result.rowcount > 0:
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    return jsonify({'error': 'Unauthorized: Admins only'}), 403

def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('role', None)  # Clear role from session
        return jsonify({'message': 'Logged out successfully'}), 200
    else:
        return jsonify({'message': 'No user is currently logged in'}), 400
