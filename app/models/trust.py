from app.database import db

class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='documents')
    
    document_type = db.Column(db.String(50), nullable=False) # ID_PROOF, BUSINESS_LICENSE, VEHICLE_REGISTRATION
    file_path = db.Column(db.String(255), nullable=False) # Stored outside static folder for privacy
    
    status = db.Column(db.String(20), default="PENDING") # PENDING, VERIFIED, REJECTED
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f"<Document {self.document_type} for User {self.user_id}>"

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='reviews')
    
    entity_type = db.Column(db.String(50), nullable=False) # HOTEL, RESTAURANT, TEMPLE, DRIVER
    entity_id = db.Column(db.Integer, nullable=False)
    
    rating = db.Column(db.Integer, nullable=False) # 1 to 5
    content = db.Column(db.Text)
    
    status = db.Column(db.String(20), default="PENDING") # PENDING, APPROVED, REJECTED
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Review {self.rating} stars for {self.entity_type} {self.entity_id}>"

class ClaimRequest(db.Model):
    __tablename__ = "claim_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='claim_requests')
    
    entity_type = db.Column(db.String(50), nullable=False) # HOTEL, RESTAURANT, TEMPLE
    entity_id = db.Column(db.Integer, nullable=False)
    
    message = db.Column(db.Text)
    contact_number = db.Column(db.String(50))
    status = db.Column(db.String(20), default="PENDING") # PENDING, APPROVED, REJECTED
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<ClaimRequest {self.user_id} for {self.entity_type} {self.entity_id}>"
