from flask import Blueprint, render_template, request, abort
from app.models import Restaurant, FoodItem, FoodCategory
from app.database import db

restaurants_bp = Blueprint("restaurants", __name__)

@restaurants_bp.route("/restaurants")
def restaurants_list():
    query = Restaurant.query.filter_by(verification_status="PUBLISHED")
    
    # Simple filters
    cuisine = request.args.get("cuisine")
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%"))
        
    search = request.args.get("search")
    if search:
        query = query.filter(db.or_(Restaurant.name.ilike(f"%{search}%"), Restaurant.locality.ilike(f"%{search}%")))
        
    restaurants = query.all()
    return render_template("pages/restaurants/list.html", restaurants=restaurants)

@restaurants_bp.route("/restaurants/<slug>")
def restaurant_detail(slug):
    restaurant = Restaurant.query.filter_by(slug=slug, verification_status="PUBLISHED").first_or_404()
    
    return render_template("pages/restaurants/detail.html", restaurant=restaurant)

@restaurants_bp.route("/food-items")
def food_items_list():
    query = FoodItem.query.filter_by(is_available=True)
    
    search = request.args.get("search")
    if search:
        query = query.filter(db.or_(FoodItem.name.ilike(f"%{search}%"), FoodItem.description.ilike(f"%{search}%")))
        
    items = query.all()
    return render_template("pages/restaurants/food_items.html", items=items)

@restaurants_bp.route("/restaurants/<slug>/menu")
def restaurant_menu(slug):
    restaurant = Restaurant.query.filter_by(slug=slug, verification_status="PUBLISHED").first_or_404()
    categories = FoodCategory.query.filter_by(restaurant_id=restaurant.id, is_active=True).all()
    return render_template("pages/restaurants/menu.html", restaurant=restaurant, categories=categories)
