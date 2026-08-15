from app.database import db

class DiscoveredEntity(db.Model):
    __tablename__ = "discovered_entities"

    id = db.Column(db.Integer, primary_key=True)
    source_url = db.Column(db.String(500), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False) # Temple, Place, Event, etc.
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100))
    
    extracted_data = db.Column(db.JSON)
    confidence = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.String(20), default="PENDING") # PENDING, APPROVED, REJECTED, DUPLICATE
    duplicate_of_id = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

class CollectorLog(db.Model):
    __tablename__ = "collector_logs"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, server_default=db.func.now())
    end_time = db.Column(db.DateTime)
    
    status = db.Column(db.String(20)) # RUNNING, SUCCESS, FAILED
    sources_processed = db.Column(db.Integer, default=0)
    discoveries = db.Column(db.Integer, default=0)
    errors = db.Column(db.Text)
