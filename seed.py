from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from myapp.models import db, User, Order, Project
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://learnwise_0h5s_user:2amNOFbX8dHHVvQuWu33ytJMkuz5XXnc@dpg-cveo2hjv2p9s73dorbig-a.oregon-postgres.render.com/learnwise_0h5s'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def seed_data():
    with app.app_context():
        db.create_all()

        # Clear existing data in the correct order
        print("Clearing existing data...")
        try:
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

        # Create Orders
        print("Creating orders...")
        orders = [
            Order(
                name="John Order",
                email="john@example.com",
                phone="1234567890",
                project_name="Website Development",
                project_description="A full-stack web project",
                expected_duration="2 weeks",
                project_budget=500,
                currency="USD"
            ),
            Order(
                name="Jane Order",
                email="jane@example.com",
                phone="0987654321",
                project_name="Mobile App",
                project_description="A cross-platform app",
                expected_duration="1 month",
                project_budget=1000,
                currency="USD"
            )
        ]

        db.session.add_all(orders)
        db.session.commit()
        print("Orders created.")

        # Create Projects (Fix: Ensure `project_description` is never `None`)
        print("Creating projects...")
        projects = [
            Project(
                project_name="E-commerce Platform",
                project_type="programming assistance",
                project_description="An advanced e-commerce solution with user authentication and payments.",
                link_url="https://example.com",
                file_url="https://example.com/file.pdf",  # Ensure valid file_url
                created_at=datetime.utcnow()
            ),
            Project(
                project_name="Portfolio Website",
                project_type="project handling",
                project_description="A personal portfolio website showcasing past projects.",
                link_url="https://portfolio.com",
                file_url=None,  # Ensure it's explicitly set to None if optional
                created_at=datetime.utcnow()
            )
        ]

        db.session.add_all(projects)
        db.session.commit()
        print("Projects created.")

        print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
