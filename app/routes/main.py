from flask import Blueprint, render_template, jsonify, request, Response
from math import radians, sin, cos, sqrt, atan2

from app.models import Temple
from app.utils.temple_status import get_temple_status
from app.utils.weather import get_weather
from app.utils.weather_alert import get_weather_alert


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
# SEARCH TEMPLES API
# ==========================================================

@main_bp.route("/api/temples/search")
def search_temples():

    query = request.args.get(
        "q",
        ""
    ).strip()


    temples = Temple.query.filter(
        Temple.name.ilike(
            f"%{query}%"
        )
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

@main_bp.route(
    "/api/temples/<int:id>/nearby"
)
def nearby_temples(id):

    temple = Temple.query.get_or_404(id)

    nearby = []


    for other in Temple.query.all():

        if other.id == temple.id:
            continue


        # Skip temples without coordinates

        if (
            temple.latitude is None
            or temple.longitude is None
            or other.latitude is None
            or other.longitude is None
        ):

            continue


        # ==================================================
        # HAVERSINE DISTANCE
        # ==================================================

        R = 6371


        lat1 = radians(
            temple.latitude
        )

        lon1 = radians(
            temple.longitude
        )


        lat2 = radians(
            other.latitude
        )

        lon2 = radians(
            other.longitude
        )


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

            "distance": round(
                distance,
                2
            )

        })


    # Sort nearest first

    nearby.sort(
        key=lambda x: x["distance"]
    )


    return jsonify(
        nearby[:3]
    )


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
    # XML
    # ======================================================

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