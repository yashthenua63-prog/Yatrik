from flask import Blueprint, render_template, request, jsonify
from app.models import Temple

darshan_planner_bp = Blueprint('darshan_planner', __name__)

@darshan_planner_bp.route('/darshan-planner')
def darshan_planner():
    return render_template('pages/darshan_planner.html')

@darshan_planner_bp.route('/api/darshan/plan', methods=['POST'])
def plan_darshan():
    data = request.get_json() or {}
    temple_ids = data.get('temple_ids', [])
    if not temple_ids:
        return jsonify({'error': 'No temples selected'})
    
    temples = Temple.query.filter(Temple.id.in_(temple_ids)).all()
    temples.sort(key=lambda t: getattr(t, 'longitude', 0.0) or 0.0)
    
    result = []
    for t in temples:
        result.append({
            'id': t.id,
            'name': getattr(t, 'name', ''),
            'city': getattr(t, 'city', ''),
            'morning_open': getattr(t, 'morning_open', ''),
            'evening_open': getattr(t, 'evening_open', ''),
            'expected_duration': getattr(t, 'expected_duration', '')
        })
    return jsonify(result)
