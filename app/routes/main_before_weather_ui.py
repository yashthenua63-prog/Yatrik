from flask import Blueprint, render_template, jsonify, request, Response
from math import radians, sin, cos, sqrt, atan2

from app.models import Temple
from app.utils.temple_status import get_temple_status
from app.utils.weather import get_weather


main_bp = Blueprint("main", __name__)


# ==========================================================
# WEATHER CONDITION
# ==========================================================

def get_weather_condition(code):

    weather_codes = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Foggy",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Heavy Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Light Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        80: "Rain Showers",
        81: "Moderate Rain Showers",
        82: "Heavy Rain Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Heavy Thunderstorm with Hail"
    }

    return weather_codes.get(code, "Weather Information")


# ==========================================================
# WEATHER TRAVEL ADVICE
# ==========================================================

def get_weather_advice(weather):

    if not weather or "current" not in weather:
        return {
            "level": "unknown",
            "title": "Weather information unavailable",
            "message": "Weather information is currently unavailable."
        }

    current = weather["current"]

    temperature = current.get("temperature_2m", 0)
    apparent = current.get("apparent_temperature", 0)
    precipitation = current.get("precipitation", 0)
    wind = current.get("wind_speed_10m", 0)
    code = current.get("weather_code", 0)

    # Heavy weather
    if code in [95, 96, 99]:
        return {
            "level": "danger",
            "title": "⚠️ Weather Alert",
            "message": "Thunderstorm conditions may occur. Consider postponing outdoor travel."
        }

    # Heavy rain
    if code in [65, 82]:
        return {
            "level": "danger",
            "title": "🌧️ Heavy Rain Expected",
            "message": "Travel may be uncomfortable. Carry rain protection and check conditions before leaving."
        }

    # Moderate rain
    if code in [61, 63, 80, 81]:
        return {
            "level": "warning",
            "title": "🌧️ Rain Possible",
            "message": "Rain may affect your visit. Carry an umbrella or raincoat."
        }

    # Very high apparent temperature
    if apparent >= 42:
        return {
            "level": "warning",
            "title": "🥵 High Heat",
            "message": "Feels quite hot. Prefer morning or evening darshan and stay hydrated."
        }

    # Strong wind
    if wind >= 35:
        return {
            "level": "warning",
            "title": "💨 Strong Winds",
            "message": "Strong winds are possible. Take care while travelling."
        }

    # Good conditions
    if code in [0, 1, 2, 3] and precipitation == 0:
        return {
            "level": "good",
            "title": "✅ Weather Looks Good",
            "message": "Current weather conditions look suitable for visiting."
        }

    return {
        "level": "normal",
        "title": "🌤️ Normal Conditions",
        "message": "You can visit, but keep an eye on the weather."
    }


# ==========================================================
# HOME PAGE
# ==========================================================

@main_bp.route("/")
def home():

    return render_template(
        "pages/home.html"
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

    # Darshan status
    status = get_temple_status(temple)

    # Weather
    weather = None
    weather_condition = None
    weather_advice = None

    if temple.latitude and temple.longitude:

        weather = get_weather(
            temple.latitude,
            temple.longitude
        )

        if weather and weather.get("current"):

            weather_condition = get_weather_condition(
                weather["current"].get("weather_code", 0)
            )

            weather_advice = get_weather_advice(
                weather
            )

    return render_template(
        "pages/temple_detail.html",
        temple=temple,
        status=status,
        weather=weather,
        weather_condition=weather_condition,
        weather_advice=weather_advice
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
            "closing_time": temple.closing_time,
            "latitude": temple.latitude,
            "longitude": temple.longitude
        })

    return jsonify(data)


# ==========================================================
# SEARCH TEMPLES API
# ==========================================================

@main_bp.route("/api/temples/search")
def search_temples():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    temples = Temple.query.filter(
        Temple.name.ilike(f"%{query}%")
    ).all()

    data = []

    for temple in temples:

        data.append({
            "id": temple.id,
            "name": temple.name,
            "city": temple.city,
            "description": temple.description,
            "image": temple.image,
            "opening_time": temple.opening_time,
            "closing_time": temple.closing_time,
            "latitude": temple.latitude,
            "longitude": temple.longitude
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

    for other in Temple.query.all():

        if other.id == temple.id:
            continue

        if other.latitude is None or other.longitude is None:
            continue

        # Earth radius in KM
        R = 6371

        lat1 = radians(temple.latitude)
        lon1 = radians(temple.longitude)

        lat2 = radians(other.latitude)
        lon2 = radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            +
            cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )

        distance = R * c

        nearby.append({
            "id": other.id,
            "name": other.name,
            "city": other.city,
            "image": other.image,
            "distance": round(distance, 2)
        })

    nearby.sort(
        key=lambda x: x["distance"]
    )

    return jsonify(
        nearby[:3]
    )


# ==========================================================
# WEATHER API
# ==========================================================

@main_bp.route("/api/weather/<int:id>")
def temple_weather(id):

    temple = Temple.query.get_or_404(id)

    if temple.latitude is None or temple.longitude is None:

        return jsonify({
            "success": False,
            "message": "Temple location is unavailable."
        }), 404

    weather = get_weather(
        temple.latitude,
        temple.longitude
    )

    if not weather:

        return jsonify({
            "success": False,
            "message": "Weather service is currently unavailable."
        }), 503

    current = weather.get("current", {})

    return jsonify({
        "success": True,
        "temple": temple.name,
        "location": {
            "latitude": temple.latitude,
            "longitude": temple.longitude
        },
        "weather": {
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "condition": get_weather_condition(
                current.get("weather_code", 0)
            )
        },
        "advice": get_weather_advice(weather)
    })


# ==========================================================
# ROBOTS.TXT
# ==========================================================

@main_bp.route("/robots.txt")
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

@main_bp.route("/sitemap.xml")
def sitemap():

    temples = Temple.query.all()

    base_url = "https://yatrik-rw1u.onrender.com"

    urls = []

    # Home
    urls.append(
        f"""
        <url>
            <loc>{base_url}/</loc>
            <changefreq>weekly</changefreq>
            <priority>1.0</priority>
        </url>
        """
    )

    # Temples listing
    urls.append(
        f"""
        <url>
            <loc>{base_url}/temples</loc>
            <changefreq>weekly</changefreq>
            <priority>0.9</priority>
        </url>
        """
    )

    # Individual temples
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

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>
"""

    return Response(
        sitemap_xml,
        mimetype="application/xml"
    )