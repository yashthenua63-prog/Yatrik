from flask import Blueprint, render_template, request, abort
from app.models import Hotel
from app.database import db

hotels_bp = Blueprint("hotels", __name__)

@hotels_bp.route("/hotels")
def hotels_list():
    query = Hotel.query.filter_by(verification_status="PUBLISHED")
    
    # Simple filters
    price = request.args.get("price")
    if price:
        query = query.filter(Hotel.price_range == price)
        
    hotels = query.all()
    return render_template("pages/hotels/list.html", hotels=hotels)

@hotels_bp.route("/hotels/<slug>")
def hotel_detail(slug):
    hotel = Hotel.query.filter_by(slug=slug, verification_status="PUBLISHED").first_or_404()
    
    # In a real app we would query nearby temples by lat/long
    return render_template("pages/hotels/detail.html", hotel=hotel)
