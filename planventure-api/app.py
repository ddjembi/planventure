from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Basic configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///planventure.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False  # Set to True for SQL query logging

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
CORS(app, 
     origins=cors_origins.split(','),
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'])

# Initialize extensions
from extensions import db, jwt
db.init_app(app)
jwt.init_app(app)

# Import models after extensions are initialized
from models import User

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

# Routes
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to PlanVenture API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/*",
            "trips": "/trips/*"
        }
    })

@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute(db.select(1))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status
    })

# Database initialization
@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized successfully!')

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
