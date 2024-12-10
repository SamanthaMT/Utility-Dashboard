from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Enum
from datetime import datetime

db = SQLAlchemy()

#Table holding user registration data
class User(db.Model, UserMixin):
    __tablename__ = 'utility_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

#Table holding data from uploaded bills
class BillingData(db.Model):
    __tablename__ = 'billing_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utility_users.id'), nullable=False)
    upload_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    service = db.Column(Enum("Electricity", "Gas", "Water", name="service_enum"), nullable=False)
    usage_kwh = db.Column(db.Float, nullable=False)
    cost_gbp = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

user = db.relationship('User', backref='billing_data')