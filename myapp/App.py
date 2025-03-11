from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from myapp.models import db, User, Order, OrderItem, Project
from auth_routes import auth_bp
import cloudinary
import cloudinary.uploader
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key

# Cloudinary configuration
cloudinary.config(
    cloud_name='dfdqp6bdl',
    api_key='222362864812654',
    api_secret='DQZ_MxjYcApRWybwlVz1ccSq92w'
)

# Upload preset name (replace with your actual preset name)
UPLOAD_PRESET = 'learnwise'

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

    file_url = None
    if file and file.filename:
        try:
            # Upload the file to Cloudinary with the upload preset
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='raw',
                upload_preset=UPLOAD_PRESET  # Include the upload preset here
            )
            file_url = upload_result['secure_url']
        except Exception as e:
            return jsonify({"error": f"File upload failed: {str(e)}"}), 500

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

# ------------------ PROJECT ROUTES (NO JWT REQUIRED) ------------------
@app.route('/projects', methods=['POST'])
def create_project():
    data = request.form
    file = request.files.get('file')

    project_name = data.get('project_name')
    project_type = data.get('project_type')
    link_url = data.get('link_url', '')

    # Validate required fields
    if not project_name or not project_type:
        return jsonify({"error": "Project name and type are required"}), 400

    # Validate that either a file or a link is provided
    if not file and not link_url:
        return jsonify({"error": "Please provide either a file or a link"}), 400

    file_url = None
    if file and file.filename:
        try:
            # Upload the file to Cloudinary with the filename as the public ID
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='raw',  # Ensure raw files are handled
                public_id=file.filename.split('.')[0],  # Use filename as public ID
                upload_preset=UPLOAD_PRESET  # Use your upload preset
            )
            file_url = upload_result['secure_url']
        except Exception as e:
            return jsonify({"error": f"File upload failed: {str(e)}"}), 500

    # Save the project to the database
    new_project = Project(
        project_name=project_name,
        project_type=project_type,
        link_url=link_url if not file_url else '',  # Only save link_url if no file is uploaded
        file_url=file_url
    )

    db.session.add(new_project)
    db.session.commit()

    return jsonify({
        "message": "Project created successfully",
        "project": {
            "id": new_project.id,
            "project_name": new_project.project_name,
            "project_type": new_project.project_type,
            "link_url": new_project.link_url,
            "file_url": new_project.file_url
        }
    }), 201

    
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

        if project.file_url:
            # Extract the public ID from the Cloudinary URL
            public_id = project.file_url.split('/')[-1].split('.')[0]
            cloudinary.uploader.destroy(public_id, resource_type='raw')

        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)