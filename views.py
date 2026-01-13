from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from marshmallow import ValidationError

from app import app
from models import db, User, register_schema, login_schema



@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        "message": "Validation failed.",
        "status": 0,
        "errors": e.messages,
        "code": 400
    }), 400




@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Resource not found.",
        "status": 0,
        "data": {},
        "code": 404
    }), 404




@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "message": "Internal server error.",
        "status": 0,
        "data": {},
        "code": 500
    }), 500




@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}




# input validating
    validated_data = register_schema.load(data)

    if User.query.filter_by(email=validated_data['email']).first():
        return jsonify({
            "message": "Account already exists.",
            "status": 0,
            "data": {},
            "code": 400
        }), 400



    user = User(
        full_name=validated_data['full_name'],
        email=validated_data['email'],
        password=generate_password_hash(validated_data['password']),
        country_code=validated_data.get('country_code'),
        phone_number=validated_data.get('phone_number')
    )

    db.session.add(user)
    db.session.commit()


    return jsonify({
        "message": "Registered successfully.",
        "status": 1,
        "data": {
            "email": user.email,
            "full_name": user.full_name
        },
        "code": 201
    }), 201




@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}



# input validating
    validated_data = login_schema.load(data)

    user = User.query.filter_by(email=validated_data['email']).first()

    if not user:
        return jsonify({
            "message": "Account doesn't exist.",
            "status": 0,
            "data": {},
            "code": 401
        }), 401

    if not check_password_hash(user.password, validated_data['password']):
        return jsonify({
            "message": "Invalid password.",
            "status": 0,
            "data": {},
            "code": 401
        }), 401

    token = jwt.encode({
        "public_id": user.id,
        "user_type": user.user_type,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")



    return jsonify({
        "message": "You have logged in successfully.",
        "status": 1,
        "token": token,
        "data": {
            "country_code": user.country_code,
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number
        },
        "code": 200
    }), 200




