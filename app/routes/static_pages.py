from flask import Blueprint, render_template

static_pages_bp = Blueprint('static_pages', __name__)

@static_pages_bp.route('/about')
def about():
    return render_template('pages/static/about.html')

@static_pages_bp.route('/privacy')
def privacy():
    return render_template('pages/static/privacy.html')

@static_pages_bp.route('/terms')
def terms():
    return render_template('pages/static/terms.html')

@static_pages_bp.route('/safety')
def safety():
    return render_template('pages/static/safety.html')
