from flask import Blueprint, render_template, jsonify, request, Response
from math import radians, sin, cos, sqrt, atan2

from app.models import Temple, Place, Category, Hotel, Restaurant
from app.utils.temple_status import get_temple_status
from app.utils.weather import get_weather
from app.utils.weather_alert import get_weather_alert


main_bp = Blueprint("main", __name__)


# ==========================================================
# HOME PAGE
# ==========================================================

@main_bp.route("/")
def home():
    from datetime import date
    from app.models import Event
    temples = Temple.query.filter_by(verification_status="PUBLISHED").limit(6).all()
    hotels = Hotel.query.filter_by(verification_status="PUBLISHED").limit(3).all()
    restaurants = Restaurant.query.filter_by(verification_status="PUBLISHED").limit(3).all()
    events = Event.query.filter_by(is_published=True).filter(
        Event.event_date >= date.today()
    ).order_by(Event.event_date).limit(4).all()
    return render_template("pages/home.html",
                           temples=temples,
                           hotels=hotels,
                           restaurants=restaurants,
                           events=events)


# ==========================================================
# EXPLORE PAGE
# ==========================================================

@main_bp.route("/explore")
def explore():
    categories = Category.query.all()
    # Group places by category
    explore_data = {}
    for cat in categories:
        places = Place.query.filter_by(category_id=cat.id).all()
        if places:
            explore_data[cat.name] = places
            
    # Include temples in Explore as well
    temples = Temple.query.limit(10).all()
    explore_data["Popular Temples"] = temples

    return render_template(
        "pages/explore.html",
        explore_data=explore_data,
        categories=categories
    )

# ==========================================================
# ALL TEMPLES PAGE
# ==========================================================

@main_bp.route("/temples")
def temples():

    temples = Temple.query.all()

    return render_template(
        "pages/temples.html",
        temples=temples
    )


# ==========================================================
# TEMPLE DETAIL PAGE
# ==========================================================

@main_bp.route("/temples/<int:id>")
def temple_detail(id):

    temple = Temple.query.get_or_404(id)

    # ======================================================
    # DARSHAN STATUS
    # ======================================================

    status = get_temple_status(temple)


    # ======================================================
    # WEATHER
    # ======================================================

    weather = None
    weather_alert = None
    rain_probability = None

    try:

        if (
            temple.latitude is not None
            and temple.longitude is not None
        ):

            weather_data = get_weather(
                temple.latitude,
                temple.longitude
            )

            if weather_data:

                weather = weather_data

                # ------------------------------------------
                # WEATHER ALERT
                # ------------------------------------------

                weather_alert = get_weather_alert({
                    "weather": weather_data
                })


                # ------------------------------------------
                # CURRENT HOUR RAIN PROBABILITY
                # ------------------------------------------

                try:

                    current_time = weather_data[
                        "current"
                    ][
                        "time"
                    ]

                    # Example:
                    # 2026-08-08T11:15
                    #
                    # Convert to:
                    # 2026-08-08T11

                    current_hour = current_time[:13]


                    hourly_times = weather_data[
                        "hourly"
                    ][
                        "time"
                    ]


                    rain_probabilities = weather_data[
                        "hourly"
                    ][
                        "precipitation_probability"
                    ]


                    for index, hourly_time in enumerate(
                        hourly_times
                    ):

                        # Example:
                        # 2026-08-08T11:00
                        #
                        # becomes:
                        # 2026-08-08T11

                        if hourly_time[:13] == current_hour:

                            rain_probability = (
                                rain_probabilities[index]
                            )

                            break


                except (
                    KeyError,
                    IndexError,
                    TypeError
                ):

                    rain_probability = None


    except Exception as error:

        print(
            "Weather Error:",
            error
        )

        weather = None
        weather_alert = None
        rain_probability = None


    # ======================================================
    # RENDER TEMPLE PAGE
    # ======================================================

    return render_template(
        "pages/temple_detail.html",

        temple=temple,

        status=status,

        weather=weather,

        weather_alert=weather_alert,

        rain_probability=rain_probability
    )


# ==========================================================
# API - ALL TEMPLES
# ==========================================================

@main_bp.route("/api/temples")
def get_temples():

    temples = Temple.query.all()

    data = []

    for temple in temples:

        data.append({

            "id": temple.id,

            "name": temple.name,

            "city": temple.city,

            "description": temple.description,

            "image": temple.image,

            "opening_time": temple.opening_time,

            "closing_time": temple.closing_time

        })

    return jsonify(data)


# ==========================================================
# SEARCH API
# ==========================================================

@main_bp.route("/api/temples/search")
def search_temples():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    # Search Temples
    temples = Temple.query.filter(
        db.or_(
            Temple.name.ilike(f"%{query}%"),
            Temple.city.ilike(f"%{query}%")
        )
    ).all()

    # Search Places
    places = Place.query.filter(
        db.or_(
            Place.name.ilike(f"%{query}%"),
            Place.city.ilike(f"%{query}%"),
            Place.category.has(Category.name.ilike(f"%{query}%"))
        )
    ).all()
    
    # Search Hotels
    hotels = Hotel.query.filter(
        db.or_(
            Hotel.name.ilike(f"%{query}%"),
            Hotel.city.ilike(f"%{query}%")
        ),
        Hotel.verification_status == "PUBLISHED"
    ).all()
    
    # Search Restaurants
    restaurants = Restaurant.query.filter(
        db.or_(
            Restaurant.name.ilike(f"%{query}%"),
            Restaurant.city.ilike(f"%{query}%"),
            Restaurant.cuisine.ilike(f"%{query}%")
        ),
        Restaurant.verification_status == "PUBLISHED"
    ).all()

    data = []

    for t in temples:
        data.append({
            "id": t.id,
            "type": "temple",
            "name": t.name,
            "city": t.city,
            "description": t.description,
            "image": t.image,
            "url": f"/temples/{t.id}"
        })

    for p in places:
        data.append({
            "id": p.id,
            "type": "place",
            "name": p.name,
            "city": p.city,
            "description": p.description,
            "image": p.image,
            "url": f"/places/{p.slug}"
        })
        
    for h in hotels:
        data.append({
            "id": h.id,
            "type": "hotel",
            "name": h.name,
            "city": h.city,
            "description": h.description,
            "image": h.featured_image,
            "url": f"/hotels/{h.slug}"
        })
        
    for r in restaurants:
        data.append({
            "id": r.id,
            "type": "restaurant",
            "name": r.name,
            "city": r.city,
            "description": r.description,
            "image": r.featured_image,
            "url": f"/restaurants/{r.slug}"
        })

    return jsonify(data)


# ==========================================================
# NEARBY TEMPLES API
# ==========================================================

@main_bp.route("/api/temples/<int:id>/nearby")
def nearby_temples(id):
    temple = Temple.query.get_or_404(id)
    nearby = []

    if temple.latitude is None or temple.longitude is None:
        return jsonify([])

    lat1 = radians(temple.latitude)
    lon1 = radians(temple.longitude)
    R = 6371

    def calc_dist(lat2_deg, lon2_deg):
        lat2 = radians(lat2_deg)
        lon2 = radians(lon2_deg)
        a = sin((lat2 - lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    # Add other temples
    for other in Temple.query.all():
        if other.id == temple.id or other.latitude is None or other.longitude is None:
            continue
        dist = calc_dist(other.latitude, other.longitude)
        nearby.append({
            "id": other.id,
            "type": "temple",
            "name": other.name,
            "city": other.city,
            "image": other.image,
            "distance": round(dist, 2)
        })

    # Add places
    for place in Place.query.all():
        if place.latitude is None or place.longitude is None:
            continue
        dist = calc_dist(place.latitude, place.longitude)
        nearby.append({
            "id": place.id,
            "type": "place",
            "name": place.name,
            "city": place.city,
            "image": place.image,
            "distance": round(dist, 2)
        })
        
    # Add hotels
    for hotel in Hotel.query.filter_by(verification_status="PUBLISHED").all():
        if hotel.latitude is None or hotel.longitude is None:
            continue
        dist = calc_dist(hotel.latitude, hotel.longitude)
        nearby.append({
            "id": hotel.id,
            "type": "hotel",
            "name": hotel.name,
            "city": hotel.city,
            "image": hotel.featured_image,
            "distance": round(dist, 2)
        })
        
    # Add restaurants
    for restaurant in Restaurant.query.filter_by(verification_status="PUBLISHED").all():
        if restaurant.latitude is None or restaurant.longitude is None:
            continue
        dist = calc_dist(restaurant.latitude, restaurant.longitude)
        nearby.append({
            "id": restaurant.id,
            "type": "restaurant",
            "name": restaurant.name,
            "city": restaurant.city,
            "image": restaurant.featured_image,
            "distance": round(dist, 2)
        })

    # Sort nearest first
    nearby.sort(key=lambda x: x["distance"])

    return jsonify(nearby[:3])


# ==========================================================
# TEMPLE WEATHER API
# ==========================================================

@main_bp.route(
    "/api/temples/<int:id>/weather"
)
def temple_weather(id):

    temple = Temple.query.get_or_404(id)


    # ======================================================
    # CHECK LOCATION
    # ======================================================

    if (
        temple.latitude is None
        or temple.longitude is None
    ):

        return jsonify({

            "error":
            "Temple location is not available"

        }), 404


    # ======================================================
    # GET WEATHER
    # ======================================================

    weather = get_weather(
        temple.latitude,
        temple.longitude
    )


    if not weather:

        return jsonify({

            "error":
            "Weather service unavailable"

        }), 503


    # ======================================================
    # WEATHER ALERT
    # ======================================================

    alert = get_weather_alert({

        "weather": weather

    })


    return jsonify({

        "temple":
        temple.name,

        "city":
        temple.city,

        "weather":
        weather,

        "alert":
        alert

    })


# ==========================================================
# ROBOTS.TXT
# ==========================================================

@main_bp.route(
    "/robots.txt"
)
def robots_txt():

    robots = """User-agent: *
Allow: /

Sitemap: https://yatrik-rw1u.onrender.com/sitemap.xml
"""


    return Response(
        robots,
        mimetype="text/plain"
    )


# ==========================================================
# XML SITEMAP
# ==========================================================

@main_bp.route(
    "/sitemap.xml"
)
def sitemap():

    temples = Temple.query.all()


    base_url = (
        "https://yatrik-rw1u.onrender.com"
    )


    urls = []


    # ======================================================
    # HOME
    # ======================================================

    urls.append(
        f"""
        <url>
            <loc>{base_url}/</loc>
            <changefreq>weekly</changefreq>
            <priority>1.0</priority>
        </url>
        """
    )


    # ======================================================
    # TEMPLES PAGE
    # ======================================================

    urls.append(
        f"""
        <url>
            <loc>{base_url}/temples</loc>
            <changefreq>weekly</changefreq>
            <priority>0.9</priority>
        </url>
        """
    )


    # ======================================================
    # INDIVIDUAL TEMPLES
    # ======================================================

    for temple in temples:

        urls.append(
            f"""
            <url>
                <loc>{base_url}/temples/{temple.id}</loc>
                <changefreq>weekly</changefreq>
                <priority>0.8</priority>
            </url>
            """
        )


    # ======================================================
    # EXPLORE PAGE
    # ======================================================

    urls.append(
        f"""
        <url>
            <loc>{base_url}/explore</loc>
            <changefreq>weekly</changefreq>
            <priority>0.9</priority>
        </url>
        """
    )
    
    # ======================================================
    # PLACES
    # ======================================================
    places = Place.query.all()
    for place in places:
        urls.append(
            f"""
            <url>
                <loc>{base_url}/places/{place.slug}</loc>
                <changefreq>weekly</changefreq>
                <priority>0.8</priority>
            </url>
            """
        )

    # ======================================================
    # HOTELS
    # ======================================================
    hotels = Hotel.query.filter_by(verification_status="PUBLISHED").all()
    for h in hotels:
        urls.append(
            f"""
            <url>
                <loc>{base_url}/hotels/{h.slug}</loc>
                <changefreq>weekly</changefreq>
                <priority>0.8</priority>
            </url>
            """
        )
        
    # ======================================================
    # RESTAURANTS
    # ======================================================
    restaurants = Restaurant.query.filter_by(verification_status="PUBLISHED").all()
    for r in restaurants:
        urls.append(
            f"""
            <url>
                <loc>{base_url}/restaurants/{r.slug}</loc>
                <changefreq>weekly</changefreq>
                <priority>0.8</priority>
            </url>
            """
        )

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>

<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
>

{''.join(urls)}

</urlset>
"""


    return Response(
        sitemap_xml,
        mimetype="application/xml"
    )


from app.models import Review
from flask_login import current_user, login_required
from app.database import db

@main_bp.route("/api/reviews/submit", methods=["POST"])
@login_required
def submit_review():
    data = request.json
    
    entity_type = data.get("entity_type")
    entity_id = data.get("entity_id")
    rating = data.get("rating")
    content = data.get("content")
    
    if not all([entity_type, entity_id, rating]):
        return jsonify({"error": "Missing required fields"}), 400
        
    review = Review(
        user_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
        rating=int(rating),
        content=content,
        status="PENDING"
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({"message": "Review submitted successfully and is pending moderation."})

# ==========================================================
# BRAJ CIRCUIT
# ==========================================================

@main_bp.route("/braj-circuit")
def braj_circuit():
    places = Place.query.filter_by(verification_status='PUBLISHED').all()
    temples = Temple.query.filter_by(verification_status='PUBLISHED').all()
    
    cities_data = {}
    for item in places + temples:
        city = item.city
        if not city:
            city = "Other"
        if city not in cities_data:
            cities_data[city] = []
        cities_data[city].append(item)
        
    return render_template("pages/braj_circuit.html", cities_data=cities_data)