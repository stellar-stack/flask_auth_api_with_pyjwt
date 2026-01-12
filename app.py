from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from marshmallow import Schema, fields, validate, ValidationError


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError("SECRET_KEY environment variable not set!")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    country_code = db.Column(db.Integer)
    phone_number = db.Column(db.String(20))
    user_type = db.Column(db.String(20), default='AppUser')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

class RegisterSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=2))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    country_code = fields.Integer(required=False)
    phone_number = fields.String(required=False, validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

register_schema = RegisterSchema()
login_schema = LoginSchema()

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


if __name__ == '__main__':
    app.run(debug=True)
