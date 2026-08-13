from flask import Blueprint, jsonify, request, render_template
from app.models import Trip, TripItem, Temple, Place
from app.database import db
from app.routes.user import get_session_id

planner_bp = Blueprint("planner", __name__)

@planner_bp.route("/planner")
def planner_page():
    return render_template("pages/trip_planner.html")

@planner_bp.route("/api/planner/trips", methods=["GET", "POST"])
def manage_trips():
    sid = get_session_id()
    if request.method == "GET":
        trips = Trip.query.filter_by(session_id=sid).order_by(Trip.created_at.desc()).all()
        data = []
        for trip in trips:
            items = []
            for item in trip.items:
                items.append({
                    "id": item.id,
                    "temple_id": item.temple_id,
                    "place_id": item.place_id,
                    "custom_name": item.custom_name,
                    "planned_time": item.planned_time,
                    "order_index": item.order_index,
                    "name": item.temple.name if item.temple else (item.place.name if item.place else item.custom_name)
                })
            data.append({
                "id": trip.id,
                "name": trip.name,
                "items": items
            })
        return jsonify(data)
        
    elif request.method == "POST":
        data = request.json
        name = data.get("name", "My Trip")
        trip = Trip(session_id=sid, name=name)
        db.session.add(trip)
        db.session.commit()
        return jsonify({"id": trip.id, "name": trip.name, "items": []})

@planner_bp.route("/api/planner/trips/<int:trip_id>/items", methods=["POST"])
def add_trip_item(trip_id):
    sid = get_session_id()
    trip = Trip.query.filter_by(id=trip_id, session_id=sid).first_or_404()
    
    data = request.json
    item_type = data.get("type")
    item_id = data.get("id")
    custom_name = data.get("custom_name")
    
    # Calculate order index
    order_index = len(trip.items)
    
    item = TripItem(trip_id=trip.id, order_index=order_index)
    if item_type == "temple":
        item.temple_id = item_id
    elif item_type == "place":
        item.place_id = item_id
    else:
        item.custom_name = custom_name
        
    db.session.add(item)
    db.session.commit()
    
    return jsonify({"status": "success", "id": item.id})

@planner_bp.route("/api/planner/trips/<int:trip_id>/items/<int:item_id>", methods=["DELETE"])
def remove_trip_item(trip_id, item_id):
    sid = get_session_id()
    trip = Trip.query.filter_by(id=trip_id, session_id=sid).first_or_404()
    item = TripItem.query.filter_by(id=item_id, trip_id=trip.id).first_or_404()
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({"status": "success"})
