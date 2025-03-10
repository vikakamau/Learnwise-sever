from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from myapp.models import db, User, Order, OrderItem, Project
from auth_routes import auth_bp
from werkzeug.utils import secure_filename
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

# ------------------ ORDER ROUTES ------------------

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.form
    file = request.files.get('file')

    required_fields = ['name', 'email', 'phone', 'project_name', 'project_description', 'expected_duration', 'project_budget', 'currency']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Handle file upload
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    file_url = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        file_url = file_path

    try:
        full_budget = f"{data['currency']} {data['project_budget']}"

        new_order = Order(
            user_id=data.get('user_id'),
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            project_name=data['project_name'],
            project_description=data['project_description'],
            expected_duration=data['expected_duration'],
            project_budget=full_budget,
            file_url=file_url
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"message": "Order created successfully", "order": new_order.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

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

# ------------------ PROJECT ROUTES (NO JWT REQUIRED) ------------------

@app.route('/projects', methods=['POST'])
def create_project():
    try:
        data = request.form
        file = request.files.get('file')

        project_name = data.get('project_name')
        link_url = data.get('link_url', '')

        if not project_name:
            return jsonify({"error": "Project name is required"}), 400

        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        file_url = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            file_url = file_path

        new_project = Project(
            project_name=project_name,
            link_url=link_url,
            file_url=file_url
        )

        db.session.add(new_project)
        db.session.commit()

        return jsonify({"message": "Project created successfully", "project": new_project.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects]), 200

@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict()), 200

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)

        if project.file_url and os.path.exists(project.file_url):
            os.remove(project.file_url)

        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ------------------ FILE UPLOAD ROUTE ------------------

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
