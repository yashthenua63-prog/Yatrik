from app.database import db

class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))

    # Basic timings
    opening_time = db.Column(db.String(20))
    closing_time = db.Column(db.String(20))
    
    # Location
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    verification_status = db.Column(db.String(20), default="PUBLISHED") # DRAFT, PENDING, VERIFIED, PUBLISHED, REJECTED
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Trust / Info
    official_website = db.Column(db.String(255))
    expected_duration = db.Column(db.String(50)) # e.g. "1-2 hours"
    best_time_to_visit = db.Column(db.String(100)) # e.g. "Early morning"
    important_notes = db.Column(db.Text)


    category = db.relationship("Category", backref="places")

    def __repr__(self):
        return f"<Place {self.name}>"
