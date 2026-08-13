from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import SupportTicket
from app.database import db
from flask_login import current_user

support_bp = Blueprint('support_bp', __name__, url_prefix='/support')

@support_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        category = request.form.get('category')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        ticket = SupportTicket(category=category, subject=subject, message=message)
        if current_user.is_authenticated:
            ticket.user_id = current_user.id
        else:
            ticket.contact_name = request.form.get('contact_name')
            ticket.contact_email = request.form.get('contact_email')
            
        db.session.add(ticket)
        db.session.commit()
        
        flash('Thank you. We will respond within 24 hours.')
        return redirect(url_for('support_bp.contact'))
        
    return render_template('pages/support.html')
