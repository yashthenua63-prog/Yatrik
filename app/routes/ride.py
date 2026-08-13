from flask import Blueprint, render_template, request, jsonify
from app.models import Driver, Ride, FareRule
from app.database import db
from app.routes.user import get_session_id

ride_bp = Blueprint("ride", __name__)

@ride_bp.route("/ride")
def ride_page():
    return render_template("pages/ride.html")

@ride_bp.route("/api/ride/estimate", methods=["POST"])
def estimate_fare():
    data = request.json
    distance = data.get("distance_km", 0)
    vehicle_type = data.get("vehicle_type", "E-Rickshaw")
    
    rule = FareRule.query.filter_by(vehicle_type=vehicle_type, active=True).first()
    if not rule:
        return jsonify({"error": "No fare rule available for this vehicle type"}), 400
        
    estimated = rule.base_fare + (distance * rule.per_km_rate)
    return jsonify({"estimated_fare": round(estimated, 2)})

@ride_bp.route("/api/ride/request", methods=["POST"])
def request_ride():
    data = request.json
    pickup = data.get("pickup")
    destination = data.get("destination")
    distance = data.get("distance_km")
    estimated_fare = data.get("estimated_fare")
    
    if not pickup or not destination:
        return jsonify({"error": "Pickup and destination required"}), 400
        
    sid = get_session_id()
    
    # 1. Honest fallback: Find available driver
    # Driver must be ONLINE and VERIFIED
    available_driver = Driver.query.filter_by(status="ONLINE", verification_status="VERIFIED").first()
    
    if not available_driver:
        # Save ride as failed MVP
        ride = Ride(
            session_id=sid,
            pickup=pickup,
            destination=destination,
            distance_km=distance,
            estimated_fare=estimated_fare,
            status="NO_DRIVER_AVAILABLE"
        )
        db.session.add(ride)
        db.session.commit()
        
        return jsonify({
            "status": "NO_DRIVER_AVAILABLE", 
            "message": "No driver currently available. Please try again later."
        })
        
    # 2. Driver found!
    available_driver.status = "BUSY" # Lock driver
    ride = Ride(
        session_id=sid,
        driver_id=available_driver.id,
        pickup=pickup,
        destination=destination,
        distance_km=distance,
        estimated_fare=estimated_fare,
        status="ACCEPTED"
    )
    
    db.session.add(ride)
    db.session.commit()
    
    return jsonify({
        "status": "ACCEPTED",
        "ride_id": ride.id,
        "driver_name": available_driver.name,
        "vehicle_number": available_driver.vehicle_number
    })
