from app.database import db

class Hotel(db.Model):
    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    owner = db.relationship('User', backref='hotels')
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Location
    address = db.Column(db.String(255))
    locality = db.Column(db.String(100))
    city = db.Column(db.String(100), default="Vrindavan")
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Contact
    phone = db.Column(db.String(50))
    official_website = db.Column(db.String(255))
    booking_url = db.Column(db.String(255))
    
    # Details
    price_range = db.Column(db.String(50))
    amenities = db.Column(db.String(255)) # comma separated
    
    # Media
    featured_image = db.Column(db.String(255))
    
    # Status
    verification_status = db.Column(db.String(20), default="DRAFT") # DRAFT, PENDING, VERIFIED, PUBLISHED, REJECTED
    
    # Audit
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Hotel {self.name}>"
