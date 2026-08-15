from flask import Blueprint, render_template, current_app, request
from app.models.temple import Temple
from app.models.place import Place

destinations_bp = Blueprint("destinations", __name__, url_prefix="")

@destinations_bp.route("/mathura")
def mathura_hub():
    temples = Temple.query.filter_by(city="Mathura", is_approved=True).limit(5).all()
    places = Place.query.filter_by(city="Mathura", is_approved=True).limit(5).all()
    
    seo_data = {
        "title": "Mathura Travel Guide 2026 | Places, Temples, Hotels & Itinerary | Yatrik",
        "description": "Complete travel guide to Mathura. Discover top temples like Krishna Janmabhoomi, places to visit, hotels, best time to visit and local food.",
        "canonical": f"{current_app.config['BASE_URL']}/mathura",
        "og_image": f"{current_app.config['BASE_URL']}/static/images/mathura-hub.jpg",
        "type": "TouristDestination",
        "slug": "mathura"
    }
    
    return render_template(
        "seo_hubs/mathura.html", 
        temples=temples, 
        places=places,
        seo=seo_data
    )

@destinations_bp.route("/vrindavan")
def vrindavan_hub():
    temples = Temple.query.filter_by(city="Vrindavan", is_approved=True).limit(5).all()
    places = Place.query.filter_by(city="Vrindavan", is_approved=True).limit(5).all()
    
    seo_data = {
        "title": "Vrindavan Travel Guide 2026 | Temples, Places, Timings & Itinerary | Yatrik",
        "description": "Comprehensive Vrindavan travel guide. Explore Banke Bihari, Prem Mandir, ISKCON, temple timings, itineraries, and best places to stay.",
        "canonical": f"{current_app.config['BASE_URL']}/vrindavan",
        "og_image": f"{current_app.config['BASE_URL']}/static/images/vrindavan-hub.jpg",
        "type": "TouristDestination",
        "slug": "vrindavan"
    }
    
    return render_template(
        "seo_hubs/vrindavan.html", 
        temples=temples, 
        places=places,
        seo=seo_data
    )

@destinations_bp.route("/braj")
def braj_hub():
    seo_data = {
        "title": "Braj Tourism Guide 2026 | Mathura, Vrindavan, Govardhan & Barsana",
        "description": "Explore the divine land of Braj. Travel guide covering Mathura, Vrindavan, Govardhan, Barsana, Nandgaon, Radha Kund, and major Krishna temples.",
        "canonical": f"{current_app.config['BASE_URL']}/braj",
        "type": "TouristDestination",
        "slug": "braj"
    }
    
    return render_template(
        "seo_hubs/braj.html",
        seo=seo_data
    )

@destinations_bp.route("/mathura/temples")
def mathura_temples():
    temples = Temple.query.filter_by(city="Mathura", is_approved=True).all()
    seo_data = {
        "title": "Best Temples in Mathura | Timings, History & Darshan Guide | Yatrik",
        "description": "Discover the most famous temples in Mathura including Shri Krishna Janmabhoomi and Dwarkadhish. Get darshan timings and travel tips.",
        "canonical": f"{current_app.config['BASE_URL']}/mathura/temples"
    }
    return render_template("seo_hubs/temples_list.html", temples=temples, city="Mathura", seo=seo_data)

@destinations_bp.route("/vrindavan/temples")
def vrindavan_temples():
    temples = Temple.query.filter_by(city="Vrindavan", is_approved=True).all()
    seo_data = {
        "title": "Best Temples in Vrindavan | Timings, Aarti & Darshan Guide | Yatrik",
        "description": "Complete guide to Vrindavan temples. Explore Banke Bihari, Prem Mandir, ISKCON, Radha Raman, with updated timings and visitor information.",
        "canonical": f"{current_app.config['BASE_URL']}/vrindavan/temples"
    }
    return render_template("seo_hubs/temples_list.html", temples=temples, city="Vrindavan", seo=seo_data)

@destinations_bp.route("/<city>/temples/<slug>")
def temple_detail(city, slug):
    # Query temple by slug and city
    temple = Temple.query.filter(
        Temple.city.ilike(city),
        Temple.slug == slug,
        Temple.verification_status == 'PUBLISHED'
    ).first_or_404()
        
    seo_data = {
        "title": temple.seo_title or f"{temple.name} {city.capitalize()} | Timings, Darshan & Travel Guide | Yatrik",
        "description": temple.seo_description or f"Planning to visit {temple.name} in {city.capitalize()}? Check timings, how to reach, nearby attractions, and history.",
        "canonical": temple.canonical_url or f"{current_app.config.get('BASE_URL', '')}/{city.lower()}/temples/{temple.slug}",
        "type": "TouristAttraction",
        "og_image": temple.image
    }
    
    # Fetch nearby templates
    from app.services.distance_service import calculate_distance_km
    nearby_temples = []
    if temple.latitude and temple.longitude:
        for other in Temple.query.filter(Temple.id != temple.id, Temple.verification_status == 'PUBLISHED').all():
            if other.latitude and other.longitude:
                dist = calculate_distance_km(temple.latitude, temple.longitude, other.latitude, other.longitude)
                if dist is not None:
                    nearby_temples.append((other, dist))
        nearby_temples.sort(key=lambda x: x[1])
        nearby_temples = [t[0] for t in nearby_temples[:4]]

    return render_template("seo_hubs/temple_detail.html", temple=temple, seo=seo_data, nearby_temples=nearby_temples)
