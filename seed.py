from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
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

        # Clear existing data to avoid foreign key violations
        print("Clearing existing data...")
        try:
            db.session.query(OrderItem).delete()
            db.session.query(Order).delete()
            db.session.query(Project).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("Existing data cleared.")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data: {e}")
            return

        # Create Users
        print("Creating users...")
        users = [
            User(username="admin", email="admin@gmail.com", password_hash=generate_password_hash("admin123"), is_admin=True),
            User(username="john_doe", email="john@gmail.com", password_hash=generate_password_hash("password")),
            User(username="jane_doe", email="jane@gmail.com", password_hash=generate_password_hash("password")),
        ]

        for user in users:
            existing_user = User.query.filter_by(username=user.username).first()
            if existing_user:
                print(f"User {user.username} already exists. Skipping...")
            else:
                db.session.add(user)

        db.session.commit()
        print("Users created.")

        # Fetch actual user IDs
        admin_user = User.query.filter_by(username="admin").first()
        john_user = User.query.filter_by(username="john_doe").first()
        jane_user = User.query.filter_by(username="jane_doe").first()

        # Create Orders
        print("Creating orders...")
        order1 = Order(
            user_id=john_user.id,
            name="John Order",
            email="john@example.com",
            phone="1234567890",
            project_name="Website Development",
            project_description="A full-stack web project",
            expected_duration="2 weeks",
            project_budget=500
        )
        order2 = Order(
            user_id=jane_user.id,
            name="Jane Order",
            email="jane@example.com",
            phone="0987654321",
            project_name="Mobile App",
            project_description="A cross-platform app",
            expected_duration="1 month",
            project_budget=1000
        )

        db.session.add_all([order1, order2])
        db.session.commit()
        print("Orders created.")

        # Create Order Items
        print("Creating order items...")
        item1 = OrderItem(
            order_id=order1.id,
            service_name="Frontend Development",
            service_details="HTML, CSS, JavaScript"
        )
        item2 = OrderItem(
            order_id=order2.id,
            service_name="Backend Development",
            service_details="Python, Flask, SQLAlchemy"
        )

        db.session.add_all([item1, item2])
        db.session.commit()
        print("Order items created.")

        # Create Projects
        print("Creating projects...")
        project1 = Project(
            project_name="E-commerce Platform",
            project_type = "programming assistance",
            link_url="https://example.com",
            file_url=None
        )
        project2 = Project(
            project_name="Portfolio Website",
            project_type = "project handling",
            link_url="https://portfolio.com",
            file_url=None
        )

        db.session.add_all([project1, project2])
        db.session.commit()
        print("Projects created.")

        print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed_data()



