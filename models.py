# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    status = db.Column(db.String(50))  # 有意向/保持联系/无意向
    industry = db.Column(db.String(100))
    region = db.Column(db.String(100))
    notes = db.Column(db.Text)
    last_contact = db.Column(db.String(50))

    # ✅ 改为 back_populates
    contact_records = db.relationship('ContactRecord', back_populates='customer', lazy=True)


class ContactRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    contact_time = db.Column(db.String(50))
    method = db.Column(db.String(50))  # 电话、微信、上门等
    content = db.Column(db.Text)
    emotion = db.Column(db.String(50))  # 积极、中立、消极
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ 改为 back_populates
    customer = db.relationship("Customer", back_populates="contact_records")

