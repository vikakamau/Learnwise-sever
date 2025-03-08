from myapp import create_app
from flask_migrate import Migrate
from myapp import db

app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)
