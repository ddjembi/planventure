"""
Flask extensions initialization.
This module prevents circular imports by initializing extensions separately.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
