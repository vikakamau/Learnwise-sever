from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from myapp.models import User, db  # ✅ Import only User and db, NOT app

# ✅ Define Blueprint first
auth_bp = Blueprint("auth", __name__)

# ✅ Apply CORS to allow all origins dynamically
CORS(auth_bp, supports_credentials=True)

def get_allowed_origin():
    """Dynamically get the allowed origin from the request."""
    return request.headers.get("Origin", "https://dickson4954.github.io")

# ✅ CORS Preflight Handling
@auth_bp.route("/<path:path>", methods=["OPTIONS"])
def handle_options(path):
    """Handle preflight requests for CORS."""
    response = jsonify({"message": "CORS preflight OK"})
    response.headers.update({
        "Access-Control-Allow-Origin": get_allowed_origin(),
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Credentials": "true"
    })
    return response

# ✅ User Signup
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Username already exists"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400

    hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
    new_user = User(username=data["username"], email=data["email"], password_hash=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    response = jsonify({"message": "User registered successfully"})
    response.headers["Access-Control-Allow-Origin"] = get_allowed_origin()
    return response, 201

# ✅ User Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("username") or not data.get("password"):
        return jsonify({"message": "Missing username/email or password"}), 400

    user = User.query.filter(
        (User.username == data["username"]) | (User.email == data["username"])
    ).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity={"id": user.id, "username": user.username, "is_admin": user.is_admin})

    response = jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }
    })
    response.headers["Access-Control-Allow-Origin"] = get_allowed_origin()
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response, 200

# ✅ Get User Profile
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.get(current_user["id"])

    if not user:
        return jsonify({"message": "User not found"}), 404

    response = jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    })
    response.headers["Access-Control-Allow-Origin"] = get_allowed_origin()
    return response, 200

# ✅ Update User Profile
@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user = User.query.get(current_user["id"])

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)

    if data.get("password"):
        user.password_hash = generate_password_hash(data["password"], method="pbkdf2:sha256")

    db.session.commit()

    response = jsonify({"message": "Profile updated successfully"})
    response.headers["Access-Control-Allow-Origin"] = get_allowed_origin()
    return response, 200

# ✅ User Logout
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful, clear token on client side."})
    response.headers["Access-Control-Allow-Origin"] = get_allowed_origin()
    return response, 200
