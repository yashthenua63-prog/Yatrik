from app.database import db

class SavedPlace(db.Model):
    __tablename__ = "saved_places"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False) # For anonymous users
    
    temple_id = db.Column(db.Integer, db.ForeignKey("temples.id"), nullable=True)
    place_id = db.Column(db.Integer, db.ForeignKey("places.id"), nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    temple = db.relationship("Temple")
    place = db.relationship("Place")

    def __repr__(self):
        return f"<SavedPlace {self.id}>"
