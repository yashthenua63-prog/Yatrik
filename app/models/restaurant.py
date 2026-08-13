from app.database import db

class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    owner = db.relationship('User', backref='restaurants')
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Details
    cuisine = db.Column(db.String(150))
    price_range = db.Column(db.String(50))
    timings = db.Column(db.String(100))
    
    # Location
    address = db.Column(db.String(255))
    locality = db.Column(db.String(100))
    city = db.Column(db.String(100), default="Vrindavan")
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Contact
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    menu_url = db.Column(db.String(255))
    
    # Media
    featured_image = db.Column(db.String(255))
    
    # Status
    verification_status = db.Column(db.String(20), default="DRAFT") # DRAFT, PENDING, VERIFIED, PUBLISHED, REJECTED
    
    # Audit
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class FoodCategory(db.Model):
    __tablename__ = "food_categories"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    restaurant = db.relationship('Restaurant', backref='food_categories')
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

class FoodItem(db.Model):
    __tablename__ = "food_items"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('food_categories.id'), nullable=False)
    category = db.relationship('FoodCategory', backref='items')
    
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    is_veg = db.Column(db.Boolean, default=True)
    is_available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))
