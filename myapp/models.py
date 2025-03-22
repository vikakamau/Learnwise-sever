from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationship with Order
    orders = db.relationship('Order', backref='user', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "orders": [order.to_dict() for order in self.orders]
        }


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Allows guest orders
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(110), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    project_description = db.Column(db.String(500), nullable=False)
    expected_duration = db.Column(db.String(50), nullable=False)
    project_budget = db.Column(db.Float, nullable=False)  # Changed to Float for decimal support
    currency = db.Column(db.String(10), nullable=False)
    link_url = db.Column(db.String(255), nullable=True)
    file_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Ensure non-null values

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "expected_duration": self.expected_duration,
            "project_budget": self.project_budget,
            "currency": self.currency,
            "link_url": self.link_url,
            "file_url": self.file_url,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(101), nullable=False)
    project_type = db.Column(db.String(100), nullable=False)
    project_description = db.Column(db.Text, nullable=False)  # Added project description
    link_url = db.Column(db.String(255), nullable=True)  # Made nullable
    file_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Ensure non-null values

    def to_dict(self):
        return {
            "id": self.id,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "project_description": self.project_description,
            "link_url": self.link_url,
            "file_url": self.file_url,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
