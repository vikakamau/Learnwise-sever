from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='user')


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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    items = db.relationship('OrderItem', backref='order', lazy='joined')


    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at,
            "items": [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    project_description = db.Column(db.String(500), nullable=False)
    file_url = db.Column(db.String(255), nullable=True)
    expected_duration = db.Column(db.String(20), nullable=False)
    project_budget = db.Column(db.Integer, nullable=False)


    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "file_url": self.file_url,
            "expected_duration": self.expected_duration,
            "project_budget": self.project_budget
        }


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    link_url = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255), nullable=True)


    def to_dict(self):
        return {
            "id": self.id,
            "project_name": self.project_name,
            "link_url": self.link_url,
            "file_url": self.file_url
        }



