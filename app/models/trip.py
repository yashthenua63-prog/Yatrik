from app.database import db

class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False) # For anonymous users
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    items = db.relationship("TripItem", backref="trip", cascade="all, delete-orphan", order_by="TripItem.order_index")

    def __repr__(self):
        return f"<Trip {self.name}>"

class TripItem(db.Model):
    __tablename__ = "trip_items"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    
    # Can link to either Temple or Place. We use generic nullable foreign keys.
    temple_id = db.Column(db.Integer, db.ForeignKey("temples.id"), nullable=True)
    place_id = db.Column(db.Integer, db.ForeignKey("places.id"), nullable=True)
    
    # Custom items (e.g. "Lunch")
    custom_name = db.Column(db.String(150), nullable=True)

    planned_time = db.Column(db.String(20), nullable=True) # e.g. "09:00 AM"
    order_index = db.Column(db.Integer, default=0)

    temple = db.relationship("Temple")
    place = db.relationship("Place")

    def __repr__(self):
        return f"<TripItem {self.id} for Trip {self.trip_id}>"
