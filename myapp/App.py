from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from myapp.models import db, User, Order, OrderItem, Project
from auth_routes import auth_bp
import os



app = Flask(__name__)


# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define a folder to store uploaded files


# Initialize extensions
db.init_app(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
jwt = JWTManager(app)

# Ensure tables are created before running
with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
@app.route('/orders', methods=['POST'])
def create_order():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']  # Get the uploaded file
    data = request.form  # Use form data (not JSON)

    # Create a directory if it doesn’t exist
    upload_folder = "uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save file if uploaded
    file_url = None
    if file and file.filename:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file_url = file_path  # Save file path to the database

    try:
        new_order = Order(
            user_id=data.get('user_id'),
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            project_name=data['project_name'],
            project_description=data['project_description'],
            expected_duration=data['expected_duration'],
            project_budget=data['project_budget'],
            file_url=file_url  # Save file path
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify(new_order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = os.path.abspath(app.config['UPLOAD_FOLDER'])  # Ensure absolute path
    return send_from_directory(upload_folder, filename)


@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders]), 200

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ------------------ ORDER ITEM ROUTES ------------------
@app.route('/order_items', methods=['POST'])
def create_order_item():
    data = request.json
    try:
        new_item = OrderItem(
            order_id=data['order_id'],
            service_name=data['service_name'],
            service_details=data['service_details']
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/order_items/<int:item_id>', methods=['DELETE'])
def delete_order_item(item_id):
    try:
        item = OrderItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Order item deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ------------------ PROJECT ROUTES ------------------
@app.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    try:
        new_project = Project(
            project_name=data['project_name'],
            link_url=data['link_url'],
            file_url=data.get('file_url')
        )
        db.session.add(new_project)
        db.session.commit()
        return jsonify(new_project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects]), 200

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
