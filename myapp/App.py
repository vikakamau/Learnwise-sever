from flask import Flask, request, jsonify
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from myapp.models import db, User, Order, Project
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from auth_routes import auth_bp
import cloudinary
import cloudinary.uploader
import os


app = Flask(__name__)


# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://learnwise_0h5s_user:2amNOFbX8dHHVvQuWu33ytJMkuz5XXnc@dpg-cveo2hjv2p9s73dorbig-a.oregon-postgres.render.com/learnwise_0h5s'
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


VALID_FILE_TYPES = {
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
}


# Initialize extensions
db.init_app(app)
CORS(app, resources={r"/*": {"origins": ["https://dickson4954.github.io", "http://localhost:3000"]}}, supports_credentials=True)
jwt = JWTManager(app)
migrate = Migrate(app, db)


# Ensure tables are created before running
with app.app_context():
    db.create_all()


# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')


# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'vikakamau72@gmail.com'
EMAIL_PASSWORD = 'xaqn twdn myqd lobb'


logging.basicConfig(level=logging.DEBUG)


@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        data = request.json
        logging.debug(f"Received data: {data}")


        # Extract form data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        message = data.get('message')


        # Validate required fields
        if not all([first_name, last_name, email, message]):
            return jsonify({"error": "All fields are required"}), 400


        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = f'New Contact Form Submission from {first_name} {last_name}'


        body = f"""
        Name: {first_name} {last_name}
        Email: {email}
        Message: {message}
        """
        msg.attach(MIMEText(body, 'plain'))


        # Send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
        server.quit()


        return jsonify({'message': 'Email sent successfully!'}), 200


    except smtplib.SMTPException as e:
        logging.error(f"SMTP error: {e}")
        return jsonify({'message': f'Failed to send email: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500




# ------------------ ORDER ROUTES ------------------


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.form
    file = request.files.get('file')
    link_url = data.get('link_url', '')
    required_fields = ['name', 'email', 'phone', 'project_name', 'project_description', 'expected_duration', 'currency', 'project_budget']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Validate that either a file or a link is provided
    if not file and not link_url:
        return jsonify({"error": "Please provide either a file or a link"}), 400

    # Validate file type if a file is uploaded
    if file:
        file_type = file.content_type
        if file_type not in VALID_FILE_TYPES:
            return jsonify({"error": "Invalid file type. Only PDF and DOCX files are allowed."}), 400

        # Optionally, you can also check the file extension
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[-1].lower()
        if file_extension not in VALID_FILE_TYPES.values():
            return jsonify({"error": "Invalid file extension. Only PDF and DOCX files are allowed."}), 400

        # Proceed with file upload to Cloudinary or any other processing
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='raw',
                public_id=filename,  # Use the original filename
                upload_preset=UPLOAD_PRESET
            )
            file_url = upload_result['secure_url']
        except Exception as e:
            return jsonify({"error": f"File upload failed: {str(e)}"}), 500
    else:
        file_url = None

    try:
        project_budget = float(data['project_budget'])
        currency = data['currency']

        new_order = Order(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            project_name=data['project_name'],
            project_description=data['project_description'],
            expected_duration=data['expected_duration'],
            project_budget=project_budget,
            currency=currency,
            link_url=link_url if not file_url else '',
            file_url=file_url
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            "message": "Order created successfully",
            "order": {
                "id": new_order.id,
                "name": new_order.name,
                "email": new_order.email,
                "phone": new_order.phone,
                "project_name": new_order.project_name,
                "project_description": new_order.project_description,
                "expected_duration": new_order.expected_duration,
                "project_budget": new_order.project_budget,
                "link_url": new_order.link_url,
                "file_url": new_order.file_url
            }
        }), 201

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
    project_description = data.get('project_description', '')  # Ensure it defaults to an empty string
    link_url = data.get('link_url', '')

    # Validate required fields
    if not project_name or not project_type:
        return jsonify({"error": "Project name and type are required"}), 400

    # Validate that either a file or a link is provided
    if not file and not link_url:
        return jsonify({"error": "Please provide either a file or a link"}), 400

    file_url = None  # Default file_url

    # Validate file type if a file is uploaded
    if file:
        file_type = file.content_type
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[-1].lower()

        if file_type not in VALID_FILE_TYPES or file_extension not in VALID_FILE_TYPES.values():
            return jsonify({"error": "Invalid file type. Only PDF and DOCX files are allowed."}), 400

        # Upload file to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='raw',
                public_id=filename,  # Use the original filename
                upload_preset=UPLOAD_PRESET
            )
            file_url = upload_result['secure_url']
        except Exception as e:
            return jsonify({"error": f"File upload failed: {str(e)}"}), 500

    # Save the project to the database
    new_project = Project(
        project_name=project_name,
        project_type=project_type,
        project_description=project_description,  # Ensuring it's never NULL
        link_url=link_url if not file_url else '',  # Only save link_url if no file is uploaded
        file_url=file_url
    )

    try:
        db.session.add(new_project)
        db.session.commit()
        return jsonify({
            "message": "Project created successfully",
            "project": {
                "id": new_project.id,
                "project_name": new_project.project_name,
                "project_type": new_project.project_type,
                "project_description": new_project.project_description,
                "link_url": new_project.link_url,
                "file_url": new_project.file_url
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

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

