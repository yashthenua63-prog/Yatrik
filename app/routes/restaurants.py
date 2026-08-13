from flask import Blueprint, render_template, request, abort
from app.models import Restaurant
from app.database import db

restaurants_bp = Blueprint("restaurants", __name__)

@restaurants_bp.route("/restaurants")
def restaurants_list():
    query = Restaurant.query.filter_by(verification_status="PUBLISHED")
    
    # Simple filters
    cuisine = request.args.get("cuisine")
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%"))
        
    restaurants = query.all()
    return render_template("pages/restaurants/list.html", restaurants=restaurants)

@restaurants_bp.route("/restaurants/<slug>")
def restaurant_detail(slug):
    restaurant = Restaurant.query.filter_by(slug=slug, verification_status="PUBLISHED").first_or_404()
    
    return render_template("pages/restaurants/detail.html", restaurant=restaurant)
