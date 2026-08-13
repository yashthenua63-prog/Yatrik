from app.database import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)

    # Hindu calendar info (never fabricate)
    hindu_calendar_name = db.Column(db.String(150))    # e.g. "3rd day of Bhadra (Shukla Paksha)"

    # Gregorian date for the current year (admin sets this each year)
    event_date = db.Column(db.Date, nullable=True)
    event_end_date = db.Column(db.Date, nullable=True)  # For multi-day events

    # Location
    location = db.Column(db.String(255))
    city = db.Column(db.String(100), default="Vrindavan")

    # Content
    travel_info = db.Column(db.Text)        # How to reach / what to expect
    special_notes = db.Column(db.Text)      # Verified crowd/timing notes

    # Featured image
    image = db.Column(db.String(255))

    # Publishing
    is_published = db.Column(db.Boolean, default=False)

    # Audit
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Event {self.title}>"
