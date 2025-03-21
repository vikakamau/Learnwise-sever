from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate

db = SQLAlchemy()
migrate = Migrate()  # Initialize Migrate

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://learnwise_83bm_user:EcLLbmj28dxHhlw1lBCEppV9YhNqbrhi@dpg-cvednjtsvqrc73f9qt1g-a.oregon-postgres.render.com/learnwise_83bm'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate

    return app
