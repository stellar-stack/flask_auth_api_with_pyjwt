from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# In-memory user store (replace with DB in production)
users = {}

# REGISTER API
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')

    if email in users:
        return jsonify({
            "message": "Account already exists.",
            "status": 0,
            "data": {},
            "code": 400
        }), 400

    users[email] = {
        "full_name": data.get('full_name'),
        "email": email,
        "country_code": data.get('country_code'),
        "phone_number": data.get('phone_number'),
        "password": generate_password_hash(data.get('password')),
        "user_type": "AppUser",
        "public_id": len(users) + 1
    }

    return jsonify({
        "message": "Registered successfully.",
        "status": 1,
        "data": {},
        "code": 201
    }), 201


# LOGIN API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users.get(email)

    if not user:
        return jsonify({
            "message": "Account doesn't exist.",
            "status": 0,
            "data": {},
            "code": 401
        }), 401

    if not check_password_hash(user['password'], password):
        return jsonify({
            "message": "Invalid password.",
            "status": 0,
            "data": {},
            "code": 401
        }), 401

    token = jwt.encode({
        "public_id": user['public_id'],
        "User_Type": user['user_type'],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "message": "You have logged in successfully.",
        "status": 1,
        "token": token,
        "data": {
            "country_code": user['country_code'],
            "email": user['email'],
            "full_name": user['full_name'],
            "phone_number": user['phone_number']
        },
        "code": 200
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
