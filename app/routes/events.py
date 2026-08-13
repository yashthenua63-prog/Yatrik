from flask import Blueprint, render_template
from app.models import Event
from datetime import date

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('')
def list_events():
    events = Event.query.filter_by(is_published=True).order_by(Event.event_date).all()
    today = date.today()
    upcoming = [e for e in events if getattr(e, 'event_date', None) and e.event_date >= today]
    return render_template('pages/events/list.html', events=events, upcoming=upcoming)

@events_bp.route('/<slug>')
def event_detail(slug):
    event = Event.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('pages/events/detail.html', event=event)
