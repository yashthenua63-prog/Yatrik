from app.database import db


class LocalSeller(db.Model):
    __tablename__ = "local_sellers"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    owner = db.relationship('User', backref='local_sellers')

    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)

    # Category: SWEETS / PUJA_ITEMS / MALA / POSHAK / HANDICRAFTS / SANJHI / SOUVENIRS / OTHER
    category = db.Column(db.String(50), nullable=False)

    description = db.Column(db.Text)
    speciality = db.Column(db.String(255))   # Admin-verified only

    # Location
    address = db.Column(db.String(255))
    locality = db.Column(db.String(100))
    city = db.Column(db.String(100), default="Vrindavan")
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Contact
    phone = db.Column(db.String(50))
    timings = db.Column(db.String(100))

    # Media
    image = db.Column(db.String(255))

    # Verification
    verification_status = db.Column(db.String(20), default='PENDING')
    # PENDING / VERIFIED / PUBLISHED / REJECTED

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<LocalSeller {self.name}>"
