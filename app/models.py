from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'utility_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class BillingData(db.Model):
    __tablename__ = 'billing_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utility_users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    usage_kwh = db.Column(db.Float, nullable=False)
    cost_gbp = db.Column(db.Float, nullable=False)

user = db.relationship('User', backref='billing_data')