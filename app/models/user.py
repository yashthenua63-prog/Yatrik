from app.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    
    role = db.Column(db.String(20), default="TRAVELER") # ADMIN, TRAVELER, DRIVER, HOTEL_PARTNER, RESTAURANT_PARTNER
    is_active = db.Column(db.Boolean, default=True)
    
    # Audit
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "ADMIN"
        
    @property
    def is_driver(self):
        return self.role == "DRIVER"

    @property
    def is_hotel_partner(self):
        return self.role == "HOTEL_PARTNER"

    @property
    def is_restaurant_partner(self):
        return self.role == "RESTAURANT_PARTNER"

    def __repr__(self):
        return f"<User {self.email}>"
