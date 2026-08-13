import uuid
from flask import Blueprint, session, jsonify, request, render_template
from app.models import SavedPlace, Temple, Place
from app.database import db

user_bp = Blueprint("user", __name__)

@user_bp.route("/saved")
def saved_page():
    return render_template("pages/saved.html")

def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]

@user_bp.route("/api/save", methods=["POST"])
def save_place():
    data = request.json
    item_id = data.get("id")
    item_type = data.get("type") # 'temple' or 'place'
    
    if not item_id or not item_type:
        return jsonify({"error": "Invalid data"}), 400
        
    sid = get_session_id()
    
    # Check if already saved
    existing = SavedPlace.query.filter_by(session_id=sid).filter(
        (SavedPlace.temple_id == item_id) if item_type == 'temple' else (SavedPlace.place_id == item_id)
    ).first()
    
    if existing:
        # Unsave
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"status": "removed"})
    else:
        # Save
        if item_type == 'temple':
            sp = SavedPlace(session_id=sid, temple_id=item_id)
        else:
            sp = SavedPlace(session_id=sid, place_id=item_id)
            
        db.session.add(sp)
        db.session.commit()
        return jsonify({"status": "saved"})

@user_bp.route("/api/saved", methods=["GET"])
def get_saved_places():
    sid = get_session_id()
    saved = SavedPlace.query.filter_by(session_id=sid).order_by(SavedPlace.created_at.desc()).all()
    
    data = []
    for sp in saved:
        if sp.temple:
            data.append({
                "id": sp.temple.id,
                "type": "temple",
                "name": sp.temple.name,
                "city": sp.temple.city,
                "image": sp.temple.image,
                "url": f"/temples/{sp.temple.id}"
            })
        elif sp.place:
            data.append({
                "id": sp.place.id,
                "type": "place",
                "name": sp.place.name,
                "city": sp.place.city,
                "image": sp.place.image,
                "url": f"/places/{sp.place.slug}"
            })
            
    return jsonify(data)
