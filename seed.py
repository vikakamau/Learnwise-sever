from myapp.models import db, User, Order, OrderItem, Project
from flask import Flask

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Seed data
def seed_data():
    with app.app_context():
        db.create_all()  # Ensure tables exist

        # Create Users
        user1 = User(username="john_doe", email="john@example.com", password_hash="hashed_password")
        user2 = User(username="jane_doe", email="jane@example.com", password_hash="hashed_password")
        
        db.session.add_all([user1, user2])
        db.session.commit()

        # Create Orders
        order1 = Order(user_id=user1.id, name="John Order", email="john@example.com", phone="1234567890")
        order2 = Order(user_id=user2.id, name="Jane Order", email="jane@example.com", phone="0987654321")
        
        db.session.add_all([order1, order2])
        db.session.commit()

        # Create Order Items
        item1 = OrderItem(order_id=order1.id, project_name="Website Development", 
                          project_description="A full-stack web project", expected_duration="2 weeks", 
                          project_budget=500)
        
        item2 = OrderItem(order_id=order2.id, project_name="Mobile App", 
                          project_description="A cross-platform app", expected_duration="1 month", 
                          project_budget=1000)

        db.session.add_all([item1, item2])
        db.session.commit()

        # Create Projects
        project1 = Project(project_name="E-commerce Platform", link_url="https://example.com", file_url=None)
        project2 = Project(project_name="Portfolio Website", link_url="https://portfolio.com", file_url=None)

        db.session.add_all([project1, project2])
        db.session.commit()

        print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
