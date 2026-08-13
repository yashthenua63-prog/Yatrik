from app.database import db


class FoodTrail(db.Model):
    __tablename__ = "food_trails"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    city = db.Column(db.String(100), default="Vrindavan")
    image = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    stops = db.relationship('FoodTrailStop', backref='trail',
                            cascade='all, delete-orphan',
                            order_by='FoodTrailStop.order_index')

    def __repr__(self):
        return f"<FoodTrail {self.title}>"


class FoodTrailStop(db.Model):
    __tablename__ = "food_trail_stops"

    id = db.Column(db.Integer, primary_key=True)
    trail_id = db.Column(db.Integer, db.ForeignKey('food_trails.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)
    order_index = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)       # What to try here (admin-curated, verified)

    restaurant = db.relationship('Restaurant')

    def __repr__(self):
        return f"<FoodTrailStop {self.id} on Trail {self.trail_id}>"
