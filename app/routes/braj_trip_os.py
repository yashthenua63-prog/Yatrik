from flask import Blueprint, render_template, request, jsonify
from app.models import Temple, Place, Hotel, Restaurant

braj_trip_os_bp = Blueprint('braj_trip_os', __name__)

@braj_trip_os_bp.route('/plan-my-trip')
def plan_my_trip():
    return render_template('pages/braj_trip_os.html')

@braj_trip_os_bp.route('/api/trip-os/generate', methods=['POST'])
def generate_trip():
    data = request.get_json() or {}
    days = data.get('days', 1)
    travel_mode = data.get('travel_mode', 'FAMILY')
    city = data.get('city')
    interests = data.get('interests', [])
    
    if city:
        temples = Temple.query.filter_by(city=city, verification_status='PUBLISHED').all()
        places = Place.query.filter_by(city=city, verification_status='PUBLISHED').all()
        hotel = Hotel.query.filter_by(city=city, verification_status='PUBLISHED').first()
        restaurants = Restaurant.query.filter_by(city=city, verification_status='PUBLISHED').limit(3).all()
    else:
        temples, places, hotel, restaurants = [], [], None, []
        
    plan = []
    for day in range(1, days + 1):
        slots = []
        if hotel and day == 1:
            slots.append({'time': '09:00', 'type': 'HOTEL', 'name': getattr(hotel, 'name', 'Recommended Hotel'), 'notes': 'Check-in'})
            
        max_stops = 3 if travel_mode == 'SENIOR' else 4
        if travel_mode == 'SPIRITUAL':
            pool = temples + places
        else:
            pool = temples + places
            
        stops_count = 0
        for i in range(max_stops):
            if not pool:
                break
            item = pool.pop(0)
            item_type = 'TEMPLE' if isinstance(item, Temple) else 'PLACE'
            slots.append({'time': f'{10 + i}:00', 'type': item_type, 'name': getattr(item, 'name', 'Stop'), 'notes': ''})
            stops_count += 1
            if travel_mode == 'SENIOR' and stops_count == 1:
                slots.append({'time': f'{10 + i}:30', 'type': 'BREAK', 'name': 'Rest Break', 'notes': 'Take a short rest'})
                
        if restaurants:
            slots.append({'time': '13:30', 'type': 'RESTAURANT', 'name': getattr(restaurants[0], 'name', 'Lunch Spot'), 'notes': 'Lunch'})
            if len(restaurants) > 1:
                slots.append({'time': '20:00', 'type': 'RESTAURANT', 'name': getattr(restaurants[1], 'name', 'Dinner Spot'), 'notes': 'Dinner'})
                
        plan.append({'day': day, 'slots': slots})
        
    return jsonify({
        'days': plan,
        'disclaimer': 'This is a suggested itinerary. Timings are approximate. Please verify locally.'
    })
