from flask import Blueprint, render_template, jsonify, request
from math import radians, sin, cos, sqrt, atan2
from app.models import Temple
from app.utils.temple_status import get_temple_status

main_bp = Blueprint("main", __name__)


# Home Page
@main_bp.route("/")
def home():
    return render_template("pages/home.html")


# API - All Temples
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



# Dynamic Temple Detail Page
@main_bp.route("/temples/<int:id>")
def temple_detail(id):

    temple = Temple.query.get_or_404(id)

    status = get_temple_status(temple)

    return render_template(
        "pages/temple_detail.html",
        temple=temple,
        status=status
    )
# Search Temples API
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
# Nearby Temples API

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


            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2


            c = 2 * atan2(sqrt(a), sqrt(1-a))


            distance = R * c



            nearby.append({

                "id": other.id,
                "name": other.name,
                "city": other.city,
                "image": other.image,
                "distance": round(distance,2)

            })



    nearby.sort(key=lambda x:x["distance"])


    return jsonify(nearby[:3])