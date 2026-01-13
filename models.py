from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    country_code = db.Column(db.Integer)
    phone_number = db.Column(db.String(20))
    user_type = db.Column(db.String(20), default='AppUser')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


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
