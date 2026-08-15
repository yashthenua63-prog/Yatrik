from flask import Blueprint, render_template, current_app, abort
from app.models import NewsArticle

news_bp = Blueprint("news", __name__)

@news_bp.route("/news/")
def news_hub():
    articles = NewsArticle.query.filter_by(status='PUBLISHED').order_by(NewsArticle.published_at.desc()).all()
    
    seo_data = {
        "title": "Latest News & Updates | Yatrik",
        "description": "Stay updated with the latest news, festival information, and temple timings for Mathura, Vrindavan, and Braj.",
        "canonical": f"{current_app.config.get('BASE_URL', '')}/news/"
    }
    
    return render_template("news/hub.html", articles=articles, seo=seo_data, location="All")

@news_bp.route("/<city>/news/")
def city_news_hub(city):
    if city.lower() not in ['mathura', 'vrindavan', 'braj']:
        abort(404)
        
    articles = NewsArticle.query.filter(
        NewsArticle.status == 'PUBLISHED',
        NewsArticle.city.ilike(city)
    ).order_by(NewsArticle.published_at.desc()).all()
    
    seo_data = {
        "title": f"Latest {city.capitalize()} News & Updates | Yatrik",
        "description": f"Stay updated with the latest {city.capitalize()} news, festival information, and temple timings.",
        "canonical": f"{current_app.config.get('BASE_URL', '')}/{city.lower()}/news/"
    }
    
    return render_template("news/hub.html", articles=articles, seo=seo_data, location=city.capitalize())

@news_bp.route("/news/<slug>/")
def news_detail(slug):
    article = NewsArticle.query.filter_by(slug=slug, status='PUBLISHED').first_or_404()
    
    seo_data = {
        "title": article.seo_title or f"{article.title} | Yatrik News",
        "description": article.seo_description or article.summary,
        "canonical": article.canonical_url or f"{current_app.config.get('BASE_URL', '')}/news/{article.slug}/",
        "type": "NewsArticle",
        "og_image": article.image
    }
    
    return render_template("news/detail.html", article=article, seo=seo_data)
