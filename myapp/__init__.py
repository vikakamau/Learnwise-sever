from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure the database (Make sure this is set)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Import and register your blueprints (if any)
    from myapp.App import main
    app.register_blueprint(main)

    return app
