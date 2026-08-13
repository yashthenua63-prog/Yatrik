from flask import Blueprint, render_template
from app.models import FoodTrail

food_trails_bp = Blueprint('food_trails', __name__, url_prefix='/food-trails')

@food_trails_bp.route('')
def list_trails():
    trails = FoodTrail.query.filter_by(is_published=True).all()
    return render_template('pages/food_trails/list.html', trails=trails)

@food_trails_bp.route('/<slug>')
def trail_detail(slug):
    trail = FoodTrail.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('pages/food_trails/detail.html', trail=trail)
