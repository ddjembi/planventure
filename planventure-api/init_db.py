"""
Database initialization script.
Run this script to create all database tables.

Usage:
    python init_db.py
"""

from app import app
from extensions import db
from models import User, Trip


def init_database():
    """Initialize the database and create all tables."""
    with app.app_context():
        # Drop all tables (optional - comment out if you want to keep existing data)
        # db.drop_all()
        # print("Dropped all existing tables.")
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Verify tables were created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")


if __name__ == '__main__':
    init_database()
