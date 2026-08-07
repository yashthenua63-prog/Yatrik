from flask import Blueprint, render_template, jsonify, request, Response
from math import radians, sin, cos, sqrt, atan2
from app.models import Temple
from app.utils.temple_status import get_temple_status


main_bp = Blueprint("main", __name__)


# ==========================================================
# HOME PAGE
# ==========================================================

@main_bp.route("/")
def home():
    return render_template("pages/home.html")


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
# DYNAMIC TEMPLE DETAIL PAGE
# ==========================================================

@main_bp.route("/temples/<int:id>")
def temple_detail(id):

    temple = Temple.query.get_or_404(id)

    status = get_temple_status(temple)

    return render_template(
        "pages/temple_detail.html",
        temple=temple,
        status=status
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
# SEARCH TEMPLES API
# ==========================================================

@main_bp.route("/api/temples/search")
def search_temples():

    query = request.args.get("q", "")

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
            "closing_time": temple.closing_time
        })

    return jsonify(data)


# ==========================================================
# NEARBY TEMPLES API
# ==========================================================

@main_bp.route("/api/temples/<int:id>/nearby")
def nearby_temples(id):

    temple = Temple.query.get_or_404(id)

    nearby = []

    for other in Temple.query.all():

        if other.id != temple.id:

            # Haversine Distance

            R = 6371

            lat1 = radians(temple.latitude)
            lon1 = radians(temple.longitude)

            lat2 = radians(other.latitude)
            lon2 = radians(other.longitude)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = (
                sin(dlat / 2) ** 2
                + cos(lat1)
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

    return jsonify(nearby[:3])


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