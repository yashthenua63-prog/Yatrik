from app.database import db

class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref='driver_profile')
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    profile_photo = db.Column(db.String(255))
    
    vehicle_type = db.Column(db.String(50)) # e.g. E-Rickshaw, Auto
    vehicle_number = db.Column(db.String(50), unique=True)
    
    status = db.Column(db.String(20), default="OFFLINE") # ONLINE, OFFLINE, BUSY
    verification_status = db.Column(db.String(20), default="PENDING") # PENDING, VERIFIED, REJECTED, SUSPENDED
    
    service_area = db.Column(db.String(100), default="Vrindavan")
    rating = db.Column(db.Float, default=5.0)
    
    # Audit
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Driver {self.name}>"

class FareRule(db.Model):
    __tablename__ = "fare_rules"
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(50), nullable=False)
    base_fare = db.Column(db.Float, default=20.0)
    per_km_rate = db.Column(db.Float, default=10.0)
    active = db.Column(db.Boolean, default=True)

class Ride(db.Model):
    __tablename__ = "rides"
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100)) # Anonymous user tracking for MVP
    
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    driver = db.relationship('Driver', backref='rides')
    
    pickup = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    
    distance_km = db.Column(db.Float)
    estimated_fare = db.Column(db.Float)
    
    status = db.Column(db.String(50), default="REQUESTED") # REQUESTED, ACCEPTED, DRIVER_ARRIVING, DRIVER_ARRIVED, STARTED, COMPLETED, CANCELLED, NO_DRIVER_AVAILABLE
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Ride {self.id} - {self.status}>"
