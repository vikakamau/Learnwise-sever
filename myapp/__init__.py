from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate

db = SQLAlchemy()
migrate = Migrate()  # Initialize Migrate

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://learnwise_0h5s_user:2amNOFbX8dHHVvQuWu33ytJMkuz5XXnc@dpg-cveo2hjv2p9s73dorbig-a.oregon-postgres.render.com/learnwise_0h5s'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate

    return app
