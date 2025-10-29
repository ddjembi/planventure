from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_current_user
from extensions import db
from models import User
from utils.password import hash_password, verify_password
from utils.jwt_helpers import generate_tokens, generate_access_token
from utils.validation import validate_email, validate_password, validate_username

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Expected JSON payload:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "first_name": "string (optional)",
        "last_name": "string (optional)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract and validate required fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Validate email
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 409
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None
        )
        new_user.set_password(password)
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Generate tokens
        tokens = generate_tokens(new_user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name
            },
            "tokens": tokens
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user.
    
    Expected JSON payload:
    {
        "email": "string",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            },
            "tokens": tokens
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.
    """
    try:
        current_user_id = get_jwt_identity()
        access_token = generate_access_token(int(current_user_id))
        
        return jsonify({
            "access_token": access_token,
            "token_type": "Bearer"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Token refresh failed: {str(e)}"}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """
    Get current authenticated user information.
    """
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get user info: {str(e)}"}), 500
