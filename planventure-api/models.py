from extensions import db
from utils.password import hash_password, verify_password

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Verify the user's password."""
        if not self.password_hash:
            return False
        return verify_password(password, self.password_hash)