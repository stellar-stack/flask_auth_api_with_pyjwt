from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_dev_secret')


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


@app.route('/register', methods=['POST'])
def register():
    data = request.json

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            "message": "Account already exists.",
            "status": 0,
            "data": {},
            "code": 400
        }), 400

    user = User(
        full_name=data['full_name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        country_code=data.get('country_code'),
        phone_number=data.get('phone_number')
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registered successfully.",
        "status": 1,
        "data": {},
        "code": 201
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({
            "message": "Account doesn't exist.",
            "status": 0,
            "data": {},
            "code": 401
        }), 401

    if not check_password_hash(user.password, data['password']):
        return jsonify({
            "message": "Invalid password.",
            "status": 0,
            "data": {},
            "code": 401
        }), 401

    token = jwt.encode({
        "public_id": user.id,
        "User_Type": user.user_type,
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
