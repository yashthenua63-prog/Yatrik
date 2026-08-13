from app.database import db


class Temple(db.Model):

    __tablename__ = "temples"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    name = db.Column(
        db.String(150),
        nullable=False
    )


    city = db.Column(
        db.String(100),
        nullable=False
    )


    description = db.Column(
        db.Text
    )


    image = db.Column(
        db.String(255)
    )


    # Old timing fields
    opening_time = db.Column(
        db.String(20)
    )


    closing_time = db.Column(
        db.String(20)
    )


    # New Darshan Timing System
    morning_open = db.Column(
        db.String(20)
    )


    morning_close = db.Column(
        db.String(20)
    )


    evening_open = db.Column(
        db.String(20)
    )


    evening_close = db.Column(
        db.String(20)
    )


    latitude = db.Column(
        db.Float
    )


    longitude = db.Column(
        db.Float
    )

    # Added fields for Trust / Info
    official_website = db.Column(db.String(255))
    expected_duration = db.Column(db.String(50))
    best_time_to_visit = db.Column(db.String(100))
    important_notes = db.Column(db.Text)


    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    verification_status = db.Column(db.String(20), default="PUBLISHED")
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)


    def __repr__(self):
        return f"<Temple {self.name}>"